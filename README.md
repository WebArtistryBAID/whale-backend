# Whale Backend

This is the backend for the ordering system for BAID's Whale Cafe. Built with FastAPI + SQLAlchemy.

## Get Started

To run in production, follow the tutorial under [BAIDWebDev](https://github.com/BAIDWebDev)/[**whale-docker**](https://github.com/BAIDWebDev/whale-docker).

To run in development:

* Ensure that you have Python available.
* Clone the repository.
* Run `pip install -r requirements.txt`.
* Export the environment variable `DATABASE_URL`, and set it to the database that you want to use (typically `sqlite:///database.db`). You need to do this every time before running.
* Run `alembic upgrade head` to apply database migrations. You only need to do this when new migrations are released.
* Run `python -m uvicorn main:app --reload`.

## Contribution

To contribute, simply open a pull request.

## License

```
    Whale is BAID's Whale Cafe's ordering system.
    Copyright (C) 2024  BAID Web Dev Team

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
