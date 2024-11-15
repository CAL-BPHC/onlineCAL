# Contributing

There aren't any formal guidelines for contributing to this project. However, the following steps are recommended:

1. Install pre-commit hooks by running `pre-commit install` in the project directory. Github Actions will run the same checks on every push to the repository.

2. Use a consistent commit format. [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) is recommended.

3. Use your personal account for contributing rather than the `CAL-BPHC` account.

## Important Note on Adding New Instruments

If the database is reset, instruments must be added in a specific order. Refer to [`config.py`](https://github.com/CAL-BPHC/onlineCAL/blob/master/server/booking_portal/config.py) for more information.

When adding a new instrument:

1. Review any [previous commit](https://github.com/CAL-BPHC/onlineCAL/commit/8693641775f9896962137c468788d0baa82b773b) where an instrument was added to get useful context.

2. Make sure to add a new entry to `form_template_dict` in `config.py` with the next integer as the key and `(InstrumentFormClass, InstrumentModelClass)` as the value.

3. After updating `config.py`, ensure the new instrument is added to the database.
