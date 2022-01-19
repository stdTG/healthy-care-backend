from core.factory.celery import get_celery_app

capp = get_celery_app()

import app.care_plans.celery.text_question
import app.care_plans.celery.number_simple
import app.care_plans.celery.number_scale
import app.care_plans.celery.date
import app.care_plans.celery.multiple_choice
import app.care_plans.celery.phone
import app.care_plans.celery.rating
import app.care_plans.celery.yes_no
import app.care_plans.celery.action_card
import app.care_plans.celery.calculator
import app.care_plans.celery.text
