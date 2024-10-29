from google.oauth2 import service_account
from googleapiclient import discovery, errors
from modules import utils
from modules.models import AirtableUser, AirtableTeam


AIRTABLE_TO_GOOGLE_TEAM_MAPPING = {
    'CM':  'communications-team@eagletrt.it',
    'DMT': 'dynamics-team@eagletrt.it',
    'HW':  'hardware-team@eagletrt.it',
    'MGT': 'management-team@eagletrt.it',
    'MT':  'mechanics-team@eagletrt.it',
    'SW':  'software-team@eagletrt.it'
}


class GoogleAdminAPI:
    def __init__(self, service_account_json: str, impersonate_admin_email: str):
        credentials = service_account.Credentials.from_service_account_file(
            service_account_json,
            scopes=[
                'https://www.googleapis.com/auth/admin.directory.user',
                'https://www.googleapis.com/auth/admin.directory.group'
            ]
        )
        delegated_credentials = credentials.with_subject(impersonate_admin_email)
        self._service = discovery.build('admin', 'directory_v1', credentials=delegated_credentials)

    def try_create_new_user(self, user: AirtableUser, temp_password: str) -> dict:
        email = utils.get_eagletrt_email(user.email)

        try:
            google_user = self._service.users().get(userKey=email).execute()
            return google_user

        except errors.HttpError as e:
            error = e.error_details[0]
            if error['reason'] == 'notFound':
                # User does not exist, create a new one
                user_body = {
                    "primaryEmail": email,
                    "name": {
                        "givenName": user.name,
                        "familyName": user.surname
                    },
                    "password": temp_password,
                    "changePasswordAtNextLogin": True
                }
                google_user = self._service.users().insert(body=user_body).execute()
                return google_user

    def add_user_to_team(self, user: AirtableUser, team: AirtableTeam):
        user_email = utils.get_eagletrt_email(user.email)
        group_email = AIRTABLE_TO_GOOGLE_TEAM_MAPPING[team.name]

        try:
            result = self._service.members().insert(
                groupKey=group_email,
                body={"email": user_email}
            ).execute()
            return result

        except errors.HttpError as e:
            error = e.error_details[0]
            if error['reason'] == 'duplicate':
                return f"User {user_email} is already in group {group_email}"

    def list_all_users(self) -> list[str]:
        try:
            response = self._service.users().list(
                customer='my_customer',
                maxResults=500,
                orderBy='email'
            ).execute()

            users = response.get('users', [])
            return [user['primaryEmail'] for user in users]

        except errors.HttpError as e:
            return []
