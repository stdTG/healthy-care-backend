import math

import pytest
from graphene import Schema
from graphene.test import Client
from graphql.execution.executors.asyncio import AsyncioExecutor

from app.patient_info.notes.gql.query import Query


@pytest.fixture
def client(context):
    yield Client(schema=Schema(query=Query), context_value=context)


class TestNoteQuery:
    def test_get_by_id_works_fine(self, client, db_note):
        user = client.execute_options['context_value']['request'].state.user

        expected = {
            'note': {
                'getById': {
                    'id': str(db_note.id),
                    'title': db_note.title,
                    'content': db_note.content,
                    'createdBy': {
                        'id_': str(user.id),
                        'firstName': user.firstName,
                        'lastName': user.lastName,
                    }
                }
            }
        }
        executed = client.execute(f'''
            {{
              note {{
                getById(id_: "{db_note.id}") {{
                  id
                  title
                  content
                  createdBy {{
                      id_
                      firstName
                      lastName
                  }}
                }}
              }}
            }}
        ''', executor=AsyncioExecutor())

        assert 'errors' not in executed
        assert executed['data'] == expected

    def test_pagination_with_default_args(self, client, db_notes_collection):
        user = client.execute_options['context_value']['request'].state.user

        default_page = 0
        default_per_page = 10
        total_items = len(db_notes_collection)
        total_pages = math.ceil(total_items / default_per_page)

        expected = {
            'note': {
                'pagination': {
                    'items': [
                        {
                            'id': str(note.id),
                            'title': note.title,
                            'content': note.content,
                            'createdBy': {
                                'id_': str(user.id),
                                'firstName': user.firstName,
                                'lastName': user.lastName,
                            }
                        } for note in db_notes_collection[:default_per_page]
                    ],
                    'pageInfo': {
                        'totalPages': total_pages,
                        'totalItems': total_items,
                        'page': default_page,
                        'perPage': default_per_page
                    }
                }
            }
        }
        executed = client.execute('''
            {
              note {
                pagination {
                  items {
                    id
                    title
                    content
                    createdBy {
                      id_
                      firstName
                      lastName
                    }
                  }
                  pageInfo {
                    totalPages
                    totalItems
                    page
                    perPage
                  }
                }
              }
            }
        ''', executor=AsyncioExecutor())

        assert 'errors' not in executed
        assert executed['data'] == expected

    def test_pagination_with_custom_args(self, client, db_notes_collection):
        user = client.execute_options['context_value']['request'].state.user

        page = 1
        per_page = 5
        total_items = len(db_notes_collection)
        total_pages = math.ceil(total_items / per_page)

        expected = {
            'note': {
                'pagination': {
                    'items': [
                        {
                            'id': str(note.id),
                            'title': note.title,
                            'content': note.content,
                            'createdBy': {
                                'id_': str(user.id),
                                'firstName': user.firstName,
                                'lastName': user.lastName,
                            }
                        } for note in
                        db_notes_collection[page * per_page:page * per_page + per_page]
                    ],
                    'pageInfo': {
                        'totalPages': total_pages,
                        'totalItems': total_items,
                        'page': page,
                        'perPage': per_page
                    }
                }
            }
        }
        executed = client.execute(f'''
            {{
              note {{
                pagination(page: {page}, perPage: {per_page}) {{
                  items {{
                    id
                    title
                    content
                    createdBy {{
                      id_
                      firstName
                      lastName
                    }}
                  }}
                  pageInfo {{
                    totalPages
                    totalItems
                    page
                    perPage
                  }}
                }}
              }}
            }}
        ''', executor=AsyncioExecutor())

        assert 'errors' not in executed
        assert executed['data'] == expected
