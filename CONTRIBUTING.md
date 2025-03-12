# Contributing

1. Each feature or bug fix should be developed in a separate branch. Changes must be merged into the `master` branch through a pull request. Direct pushes to `master` are blocked to ensure only production-ready changes are deployed. Repository admins can bypass this rule if necessary.

2. Install pre-commit hooks by running `pre-commit install` in the project directory. Github Actions will run the same checks on every push to the repository.

3. Use a consistent commit format. [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) is recommended.

4. Use your personal account for contributing rather than the `CAL-BPHC` account.

## Important Note on Adding New Instruments

If the database is reset, instruments must be added in a specific order. Refer to [`config.py`](server/booking_portal/config.py) for more information.

When adding a new instrument:

1. Review any [previous commit](https://github.com/CAL-BPHC/onlineCAL/commit/9ddd08d1f19cbd511df680a8eeb6bc0032b04b21) where an instrument was added to get useful context.

2. Make sure to add a new entry to `form_template_dict` in `config.py` with the next integer as the key and `(InstrumentFormClass, InstrumentModelClass)` as the value.

3. After updating `config.py`, you also need to add the new instrument to the `Instrument` table in the database.
