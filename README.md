# Whale Backend

This is the backend for the ordering system for BAID's Whale Cafe. Built with FastAPI + SQLAlchemy.

## Get Started

To run in production, follow the tutorial under [WebArtistryBAID](https://github.com/WebArtistryBAID)/[**whale-docker**](https://github.com/WebArtistryBAID/whale-docker).

To run in development:

* Ensure that you have at least Python 3.12 available.
* Clone the repository.
* Run `pip install -r requirements.txt`.
* Export all the following environment variables:

| Name              | Description                                                                            |
|-------------------|----------------------------------------------------------------------------------------|
| `DATABASE_URL`    | The database URL to use. Typically `sqlite:///database.db`.                            |
| `API_HOST`        | The full URL on which this API is running on, no trailing slash.                       |
| `FRONTEND_HOST`   | The full URL on which the frontend is hosted, no trailing slash.                       |
| `JWT_SECRET_KEY`  | The JWT secret key to use. You can generate one with `openssl rand -hex 32`.           |
| `SEIUE_CLIENT_ID` | The client ID received from SEIUE for authentication.                                  |
| `DEVELOPMENT`     | Set to `true` to bypass CORS protections and enable certain development-only features. |

* Run `alembic upgrade head` to apply database migrations. You only need to do this when new migrations are released.
* Run `python -m uvicorn main:app --reload`.

## Integrated Services

Project Whale is integrated with certain third-party service providers:

* SEIUE, for user authentication

## Permissions

Some users have specific permissions that allow them to access more features. These include:
* `admin.cms`: Allow entering CMS.
* `admin.manage`: Allows managing orders.

## Contribution

To contribute, simply open a pull request.

## License

```
    Whale is BAID's Whale Cafe's ordering system.
    Copyright (C) 2024  Team WebArtistry

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
