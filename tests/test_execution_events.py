import json

import pytest

from d_brain.services.execution import Execution


@pytest.mark.parametrize('message', [
    'Reconnecting... 2/5 (workspace routing discovery timed out)',
    'Model metadata for `gpt-6.1-sol` not found. Defaulting to fallback metadata; '
    'this can degrade performance and cause issues.',
])
def test_codex_recoverable_error_events_are_not_fatal(tmp_path, message):
    execution = Execution(tmp_path)
    execution.observe(json.dumps({'type': 'error', 'message': message}), 'codex')


def test_real_error_event_is_fatal_and_keeps_message(tmp_path):
    execution = Execution(tmp_path)
    with pytest.raises(RuntimeError, match='stream disconnected'):
        execution.observe(json.dumps({'type': 'error', 'message': 'stream disconnected'}), 'codex')


def test_turn_failed_is_fatal_even_when_reconnecting(tmp_path):
    execution = Execution(tmp_path)
    event = {'type': 'turn.failed', 'error': {'message': 'Reconnecting... 5/5'}}
    with pytest.raises(RuntimeError, match='Автоповтор отключён'):
        execution.observe(json.dumps(event), 'codex')
