# Whale Backend

This is the backend for the ordering system for BAID's Whale Cafe. Built with FastAPI + SQLAlchemy.

## Get Started

To run in production, follow the tutorial under [WebArtistryBAID](https://github.com/WebArtistryBAID)/[**whale-docker**](https://github.com/WebArtistryBAID/whale-docker).

To run in development:

* Ensure that you have at least Python 3.12 available.
* Clone the repository.
* Run `pip install -r requirements.txt`.
* Export the environment variable `DATABASE_URL`, and set it to the database that you want to use (typically `sqlite:///database.db`). You need to do this every time before running.
* Export the environment variable `API_HOST`, which is the full URL on which this API is running on. For example, `https://example.com/api`. No slashes are needed at the end.
* Export the environment variable `FRONTEND_HOST`, which is the full URL on which the frontend is hosted. For example, `https://example.com`. No slashes are needed at the end.
* Export the environment variable `JWT_SECRET_KEY`, and set it to the JWT secret key that you want to use. You will need to do this every time before running. You can use `openssl rand -hex 32` to generate a secret key.
* Export the environment variable `SEIUE_CLIENT_ID`, and set it to the client ID received from SEIUE for authentication. Same for `SEIUE_CLIENT_SECRET`.
* Export the environment variable `DEVELOPMENT` to `true` if you want to bypass CORS protections and enable certain development-only features.
* Run `alembic upgrade head` to apply database migrations. You only need to do this when new migrations are released.
* Run `python -m uvicorn main:app --reload`.

## Permissions

Some users have specific permissions that allow them to access more features. These include:
* `admin.statistics`: Allows viewing statistics aggregates.
* `admin.manage`: Allows managing orders.

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
