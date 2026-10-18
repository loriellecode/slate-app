-- Work items: tasks and events sent from the Workspace app to Slate, and their completion coming back.
-- Run once in the Supabase SQL editor of Slate's project (vdryzddjkvalxjbmfshh). Safe to run again.
-- No secrets here: every row belongs to the signed-in Slate account, and row-level security keeps it private.

create table if not exists public.work_items (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  wid text not null check (char_length(wid) between 1 and 120),          -- Workspace's id, e.g. "task:abc" or "event:xyz"
  kind text not null check (kind in ('task', 'event')),
  title text not null default '' check (char_length(title) <= 500),
  notes text not null default '' check (char_length(notes) <= 8000),
  due_date date,                                                           -- the day (events always have one)
  start_time text check (start_time is null or start_time ~ '^\d{2}:\d{2}$'),
  end_time text check (end_time is null or end_time ~ '^\d{2}:\d{2}$'),
  location text not null default '' check (char_length(location) <= 300),
  priority text check (priority is null or priority in ('low', 'medium', 'high')),
  project text not null default '' check (char_length(project) <= 200),
  done boolean not null default false,
  done_changed_at timestamptz not null default 'epoch',                    -- newest completion change wins
  done_by text check (done_by is null or done_by in ('workspace', 'slate')),
  deleted boolean not null default false,                                  -- removed in Workspace (kept as a marker)
  ws_updated_at timestamptz not null default now(),                        -- when Workspace last changed the fields
  updated_at timestamptz not null default now(),                           -- any change; both apps read "what changed since"
  primary key (user_id, wid)
);
create index if not exists work_items_changed on public.work_items (user_id, updated_at);

alter table public.work_items enable row level security;
drop policy if exists "own work items: read" on public.work_items;
drop policy if exists "own work items: add" on public.work_items;
drop policy if exists "own work items: change" on public.work_items;
drop policy if exists "own work items: remove" on public.work_items;
create policy "own work items: read" on public.work_items for select to authenticated using (user_id = auth.uid());
create policy "own work items: add" on public.work_items for insert to authenticated with check (user_id = auth.uid());
create policy "own work items: change" on public.work_items for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "own work items: remove" on public.work_items for delete to authenticated using (user_id = auth.uid());
revoke all on public.work_items from anon;
grant select, insert, update, delete on public.work_items to authenticated;

create or replace function public.work_items_touch() returns trigger language plpgsql as $$
begin new.updated_at := now(); return new; end $$;
drop trigger if exists work_items_touch on public.work_items;
create trigger work_items_touch before insert or update on public.work_items for each row execute function public.work_items_touch();

-- Workspace sends its tasks and events. It owns the title, date and notes; completion is kept from whichever
-- side changed it last, so a task ticked on the iPad is never un-ticked by an older copy from the computer.
create or replace function public.upsert_work_items(p_items jsonb) returns integer
language plpgsql security invoker set search_path = public as $$
declare it jsonb; n integer := 0;
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  if jsonb_typeof(p_items) <> 'array' or jsonb_array_length(p_items) > 500 then raise exception 'send at most 500 items at once'; end if;
  for it in select * from jsonb_array_elements(p_items) loop
    insert into public.work_items as w (user_id, wid, kind, title, notes, due_date, start_time, end_time, location, priority, project,
                                        done, done_changed_at, done_by, deleted, ws_updated_at)
    values (auth.uid(), it->>'wid', it->>'kind', coalesce(it->>'title', ''), coalesce(it->>'notes', ''),
            nullif(it->>'due_date', '')::date, nullif(it->>'start_time', ''), nullif(it->>'end_time', ''),
            coalesce(it->>'location', ''), nullif(it->>'priority', ''), coalesce(it->>'project', ''),
            coalesce((it->>'done')::boolean, false), coalesce((it->>'done_changed_at')::timestamptz, 'epoch'), 'workspace',
            coalesce((it->>'deleted')::boolean, false), coalesce((it->>'ws_updated_at')::timestamptz, now()))
    on conflict (user_id, wid) do update set
      kind = excluded.kind, title = excluded.title, notes = excluded.notes, due_date = excluded.due_date,
      start_time = excluded.start_time, end_time = excluded.end_time, location = excluded.location,
      priority = excluded.priority, project = excluded.project, deleted = excluded.deleted, ws_updated_at = excluded.ws_updated_at,
      done = case when excluded.done_changed_at > w.done_changed_at then excluded.done else w.done end,
      done_by = case when excluded.done_changed_at > w.done_changed_at then 'workspace' else w.done_by end,
      done_changed_at = greatest(excluded.done_changed_at, w.done_changed_at);
    n := n + 1;
  end loop;
  return n;
end $$;

-- Slate ticks or un-ticks one item. Ignored if Workspace changed it more recently.
create or replace function public.set_work_done(p_wid text, p_done boolean, p_at timestamptz) returns boolean
language plpgsql security invoker set search_path = public as $$
declare changed integer;
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  update public.work_items set done = p_done, done_changed_at = p_at, done_by = 'slate'
   where user_id = auth.uid() and wid = p_wid and done_changed_at < p_at;
  get diagnostics changed = row_count;
  return changed > 0;
end $$;

revoke all on function public.upsert_work_items(jsonb) from public, anon;
revoke all on function public.set_work_done(text, boolean, timestamptz) from public, anon;
grant execute on function public.upsert_work_items(jsonb) to authenticated;
grant execute on function public.set_work_done(text, boolean, timestamptz) to authenticated;
