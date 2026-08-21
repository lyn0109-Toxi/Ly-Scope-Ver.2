# Legacy References

`ver1-reference/` can be used as a local copied reference of the LY-Scope Ver.1 project.

The original Ver.1 project was not modified. This copy exists so Ver.2 can
preserve and migrate useful Ver.1 logic safely.

For public GitHub pushes, `ver1-reference/` is ignored because it can contain
copied source, reports, and user-like sample data. Keep it local unless there is
explicit approval to publish a sanitized reference set.

Excluded from the local copy:

- `.git`
- `__pycache__`
- `*.pyc`

Primary Ver.2 migration bridge:

- `src/adapters/ver1`
- `src/domain/market-assets`
- `src/domain/real-estate`
- `src/domain/portfolio`
- `src/domain/life-board`
