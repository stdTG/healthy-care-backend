import pytest
from graphene import Schema
from graphene.test import Client
from graphql.execution.executors.asyncio import AsyncioExecutor

from app.patient_info.notes.gql.mutation import NoteMutations
from app.patient_info.notes.models.db import Note as DbNote


@pytest.fixture
def client(context):
    yield Client(schema=Schema(mutation=NoteMutations), context_value=context)


class TestCreateNote:
    def test_mutate(self, client):
        user = client.execute_options['context_value']['request'].state.user

        title = 'note'
        content = 'content'
        patient_id = '5fd5da0d36a6434d52be193f'

        executed = client.execute(f'''
            mutation create_note {{
                create(record: {{title: "{title}", content: "{content}", patient: "{patient_id}"}}) 
                {{
                  recordId
                  record {{
                    id
                    title
                    content
                    createdBy {{
                      id_
                      firstName
                      lastName
                      role
                    }}
                  }}
              }}
            }}
        ''', executor=AsyncioExecutor())

        saved_note = DbNote.objects().first()

        expected = {
            'create': {
                'recordId': str(saved_note.id),
                'record': {
                    'id': str(saved_note.id),
                    'title': title,
                    'content': content,
                    'createdBy': {
                        'id_': str(user.id),
                        'firstName': user.firstName,
                        'lastName': user.lastName,
                        'role': user.role.upper()
                    }
                }
            }
        }

        assert 'errors' not in executed
        assert dict(executed['data']) == expected


class TestUpdateNote:
    def test_mutate(self):
        pass


class TestDeleteNote:
    def test_mutate_delete_existing_note(self, client, db_note):
        note_id = db_note.id

        expected = {
            'delete': {
                'ok': True,
                'error': None
            }
        }

        assert DbNote.objects().count() == 1

        executed = client.execute(f'''
            mutation delete_note {{
              delete(id_: "{note_id}") {{
                ok
                error {{
                  code
                  message
                }}
              }}
            }}
        ''', executor=AsyncioExecutor())

        assert DbNote.objects().count() == 0
        assert 'errors' not in executed
        assert dict(executed['data']) == expected

    def test_mutate_delete_non_existing_note(self, client):
        note_id = '5fdbb66c7014ee3a9de8913b'

        expected = {
            'delete': {
                'ok': True,
                'error': None
            }
        }
        executed = client.execute(f'''
            mutation delete_note {{
              delete(id_: "{note_id}") {{
                ok
                error {{
                  code
                  message
                }}
              }}
            }}
        ''', executor=AsyncioExecutor())

        assert 'errors' not in executed
        assert dict(executed['data']) == expected
