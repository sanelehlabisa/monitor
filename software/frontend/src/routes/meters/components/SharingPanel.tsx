import { Alert, Box, Button, CircularProgress, Stack, TextField, Typography } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';

import { ApiError, listMembers, removeMember, shareMember, type Member, type User } from '../../../lib/api';

type SharingPanelProps = {
  meterId: string;
  user: User;
  busy: boolean;
  onPendingChange: (pending: boolean) => void;
  onChanged: (left: boolean) => Promise<void>;
  onUnavailable: () => void;
};

function failure(error: unknown): string {
  if (error instanceof ApiError && error.status === 409) return 'The last member cannot leave or be removed.';
  if (error instanceof ApiError && error.status === 422) return 'Enter a valid email address.';
  if (error instanceof ApiError && error.status === 401) return 'Sign in again to manage sharing.';
  return 'Sharing could not be updated. Try again.';
}

/** Meter-local requests never delay forecasts or survive an account/meter change. */
export function SharingPanel({ meterId, user, busy, onPendingChange, onChanged, onUnavailable }: SharingPanelProps) {
  const [open, setOpen] = useState(false);
  const [members, setMembers] = useState<Member[]>([]);
  const [email, setEmail] = useState('');
  const [loaded, setLoaded] = useState(false);
  const [pending, setPending] = useState(false);
  const [needsRefresh, setNeedsRefresh] = useState(false);
  const [error, setError] = useState('');
  const generation = useRef(0);
  const mounted = useRef(false);
  const identity = `${user.id}:${meterId}`;
  const activeIdentity = useRef(identity);
  activeIdentity.current = identity;
  useEffect(() => {
    onPendingChange(pending);
    return () => onPendingChange(false);
  }, [pending, onPendingChange]);
  useEffect(() => {
    mounted.current = true;
    generation.current += 1;
    setOpen(false); setMembers([]); setEmail(''); setLoaded(false);
    setPending(false); setNeedsRefresh(false); setError('');
    return () => { mounted.current = false; generation.current += 1; };
  }, [meterId, user.id]);
  const current = (version: number) => mounted.current && version === generation.current && activeIdentity.current === identity;

  async function reload(refreshList = false) {
    const version = ++generation.current;
    setPending(true); setError('');
    try {
      const items = await listMembers(meterId);
      if (!current(version)) return;
      setMembers(items); setLoaded(true);
      if (refreshList) await onChanged(false);
      if (current(version)) setNeedsRefresh(false);
    } catch (requestError) {
      if (!current(version)) return;
      if (requestError instanceof ApiError && requestError.status === 404) { onUnavailable(); return; }
      setError(refreshList ? 'Saved, but sharing or the meter list could not be refreshed. Retry only reloads data.'
        : requestError instanceof ApiError && requestError.status === 401 ? failure(requestError) : 'Sharing could not be loaded. Try again.');
    } finally {
      if (current(version)) setPending(false);
    }
  }

  async function save(member?: Member) {
    if (busy || pending || needsRefresh || !loaded) return;
    const leaving = member?.user_id === user.id;
    if (member && !window.confirm(leaving ? 'Leave this meter? Its records will not be deleted.'
      : `Remove ${member.email} from this meter? Its records will not be deleted.`)) return;
    const version = ++generation.current;
    let written = false;
    setPending(true); setError('');
    try {
      if (member) await removeMember(meterId, member.user_id);
      else await shareMember(meterId, email);
      if (!current(version)) return;
      written = true;
      if (!member) setEmail('');
      setNeedsRefresh(true);
      if (leaving) await onChanged(true);
      else await reload(true);
    } catch (requestError) {
      if (!current(version)) return;
      if (requestError instanceof ApiError && requestError.status === 404) { onUnavailable(); return; }
      setError(written ? 'Saved, but the meter list could not be refreshed. Return to the meter list.' : failure(requestError));
    } finally {
      if (current(version)) setPending(false);
    }
  }

  function add(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (email.trim()) void save();
  }

  return (
    <Box component="details" open={open} onToggle={(event) => {
      const expanded = event.currentTarget.open;
      setOpen(expanded);
      if (expanded && !pending) void reload(needsRefresh);
    }} sx={{ borderTop: '1px solid', borderColor: 'divider', pt: 2 }}>
      <Typography component="summary" sx={{ cursor: 'pointer', fontWeight: 700 }}>Sharing</Typography>
      <Typography color="text.secondary" variant="body2" sx={{ pt: 1.5 }}>Monthly planning reminders: last day of the month, 09:00 UTC, for all members.</Typography>
      {open && <Stack spacing={1.5} sx={{ pt: 1.5 }}>
        <Typography color="text.secondary" variant="body2">Members can manage this meter. Sign-in still uses an email code.</Typography>
        {error && <Alert severity="error" action={(!loaded || needsRefresh) && (
          <Button disabled={busy || pending} onClick={() => void reload(needsRefresh)} size="small">Retry</Button>
        )}>{error}</Alert>}
        {pending && <CircularProgress aria-label="Updating sharing" size={22} />}
        <Box component="form" onSubmit={add} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TextField fullWidth required type="email" label="Member email" value={email}
            disabled={busy || pending || needsRefresh || !loaded} onChange={(event) => setEmail(event.target.value)}
            slotProps={{ htmlInput: { maxLength: 254 } }} />
          <Button type="submit" startIcon={<AddIcon />} disabled={busy || pending || needsRefresh || !loaded || !email.trim()}>Add</Button>
        </Box>
        <Stack component="ul" spacing={0.5} sx={{ m: 0, p: 0, listStyle: 'none' }}>
          {members.map((member) => <Stack component="li" key={member.user_id} direction="row" spacing={1}
            sx={{ alignItems: 'center', borderBottom: '1px solid', borderColor: 'divider', py: 0.5 }}>
            <Typography sx={{ flex: 1, minWidth: 0, overflowWrap: 'anywhere' }}>{member.email}</Typography>
            <Button size="small" color="error" disabled={busy || pending || needsRefresh}
              aria-label={member.user_id === user.id ? 'Leave meter' : `Remove ${member.email}`}
              onClick={() => void save(member)}>{member.user_id === user.id ? 'Leave' : 'Remove'}</Button>
          </Stack>)}
        </Stack>
      </Stack>}
    </Box>
  );
}
