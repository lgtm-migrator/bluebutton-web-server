from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder

import apps.logging.request_logger as logging

from apps.accounts.models import UserProfile
from apps.authorization.models import get_grant_bene_counts

from apps.dot_ext.models import (
    Application,
    get_token_bene_counts,
    get_application_counts,
    get_application_require_demographic_scopes_count,
)
from apps.fhir.bluebutton.models import get_crosswalk_bene_counts
from apps.logging.utils import format_timestamp


"""
  Logger functions for logging module
"""
logger = logging.getLogger(logging.AUDIT_GLOBAL_STATE_METRICS_LOGGER)


def log_global_state_metrics(group_timestamp=None):
    """
    For use in apps/logging/management/commands/log_global_metrics.py management command
    NOTE:  print statements are for output when run via Jenkins
    """
    print("---")
    print("---RUNNING DJANGO COMMAND:  log_global_state_metrics")
    print("---")

    start_time = datetime.utcnow().timestamp()

    crosswalk_counts = get_crosswalk_bene_counts()

    access_token_counts = get_token_bene_counts()

    grant_counts = get_grant_bene_counts()

    application_counts = get_application_counts()

    require_demographic_scopes_count = (
        get_application_require_demographic_scopes_count()
    )

    elapsed_time = round(datetime.utcnow().timestamp() - start_time, 3)

    log_dict = {
        "type": "global_state_metrics",
        "group_timestamp": group_timestamp,
        "real_bene_cnt": crosswalk_counts.get(
            "real", None
        ),  # TODO: Deprecate this duplicate name in future
        "synth_bene_cnt": crosswalk_counts.get(
            "synthetic", None
        ),  # TODO: Deprecate this duplicate name in future
        "crosswalk_real_bene_count": crosswalk_counts.get("real", None),
        "crosswalk_synthetic_bene_count": crosswalk_counts.get("synthetic", None),
        "crosswalk_table_count": crosswalk_counts.get("total", None),
        "crosswalk_archived_table_count": crosswalk_counts.get("archived_total", None),
        "crosswalk_bene_counts_elapsed": crosswalk_counts.get("elapsed", None),
        "grant_real_bene_count": grant_counts.get("real", None),
        "grant_synthetic_bene_count": grant_counts.get("synthetic", None),
        "grant_table_count": grant_counts.get("total", None),
        "grant_archived_table_count": grant_counts.get("archived_total", None),
        "grant_counts_elapsed": grant_counts.get("elapsed", None),
        "grant_real_bene_deduped_count": grant_counts.get("real_deduped", None),
        "grant_synthetic_bene_deduped_count": grant_counts.get(
            "synthetic_deduped", None
        ),
        "grant_deduped_counts_elapsed": grant_counts.get("deduped_elapsed", None),
        "grantarchived_real_bene_deduped_count": grant_counts.get(
            "archived_real_deduped", None
        ),
        "grantarchived_synthetic_bene_deduped_count": grant_counts.get(
            "archived_synthetic_deduped", None
        ),
        "grantarchived_deduped_counts_elapsed": grant_counts.get(
            "archived_deduped_elapsed", None
        ),
        "grant_and_archived_real_bene_deduped_count": grant_counts.get(
            "grant_and_archived_real_deduped", None
        ),
        "grant_and_archived_synthetic_bene_deduped_count": grant_counts.get(
            "grant_and_archived_synthetic_deduped", None
        ),
        "grant_and_archived_deduped_counts_elapsed": grant_counts.get(
            "grant_and_archived_deduped_elapsed", None
        ),
        "token_real_bene_deduped_count": access_token_counts.get("real_deduped", None),
        "token_synthetic_bene_deduped_count": access_token_counts.get(
            "synthetic_deduped", None
        ),
        "token_table_count": access_token_counts.get("total", None),
        "token_archived_table_count": access_token_counts.get("archived_total", None),
        "token_deduped_counts_elapsed": access_token_counts.get(
            "deduped_elapsed", None
        ),
        "global_apps_active_cnt": application_counts.get("active_cnt", None),
        "global_apps_inactive_cnt": application_counts.get("inactive_cnt", None),
        "global_apps_require_demographic_scopes_cnt": require_demographic_scopes_count,
        "global_state_metrics_total_elapsed": elapsed_time,
    }

    logger.info(log_dict)

    print("---")
    print("---    Wrote top level log entry: ", log_dict)
    print("---")
    print(
        "---    Top level (global_state_metrics) metrics elapsed time:  ", elapsed_time
    )
    print("---")

    applications = Application.objects.all()

    start_time = datetime.utcnow().timestamp()
    count = 0
    for app in applications:
        # Get UserProfile for application's dev user
        try:
            user_profile = UserProfile.objects.get(user=app.user)
        except UserProfile.DoesNotExist:
            user_profile = None

        access_token_counts = get_token_bene_counts(application=app)

        grant_counts = get_grant_bene_counts(application=app)

        log_dict = {
            "type": "global_state_metrics_per_app",
            "group_timestamp": group_timestamp,
            "id": app.id,
            "name": app.name,
            "created": format_timestamp(app.created),
            "updated": format_timestamp(app.updated),
            "active": app.active,
            "first_active": format_timestamp(app.first_active),
            "last_active": format_timestamp(app.last_active),
            "require_demographic_scopes": app.require_demographic_scopes,
            "real_bene_cnt": grant_counts.get(
                "real", None
            ),  # TODO: Deprecate this duplicate name in future
            "synth_bene_cnt": grant_counts.get(
                "synthetic", None
            ),  # TODO: Deprecate this duplicate name in future
            "grant_real_bene_count": grant_counts.get("real", None),
            "grant_synthetic_bene_count": grant_counts.get("synthetic", None),
            "grant_table_count": grant_counts.get("total", None),
            "grant_archived_table_count": grant_counts.get("archived_total", None),
            "grantarchived_real_bene_deduped_count": grant_counts.get(
                "archived_real_deduped", None
            ),
            "grantarchived_synthetic_bene_deduped_count": grant_counts.get(
                "archived_synthetic_deduped", None
            ),
            "grant_and_archived_real_bene_deduped_count": grant_counts.get(
                "grant_and_archived_real_deduped", None
            ),
            "grant_and_archived_synthetic_bene_deduped_count": grant_counts.get(
                "grant_and_archived_synthetic_deduped", None
            ),
            "token_real_bene_count": access_token_counts.get("real_deduped", None),
            "token_synthetic_bene_count": access_token_counts.get(
                "synthetic_deduped", None
            ),
            "token_table_count": access_token_counts.get("total", None),
            "token_archived_table_count": access_token_counts.get(
                "archived_total", None
            ),
            "user_id": app.user.id,
            "user_username": app.user.username,
            "user_date_joined": format_timestamp(app.user.date_joined),
            "user_last_login": format_timestamp(app.user.last_login),
            "user_organization": getattr(user_profile, "organization_name", None),
        }

        logger.info(log_dict, cls=DjangoJSONEncoder)

        count = count + 1

    elapsed_time = round(datetime.utcnow().timestamp() - start_time, 3)

    print("---")
    print("---    Wrote per application log entries: ", count)
    print("---")
    print(
        "---    Applications (global_state_metrics_per_app) metrics elapsed time:  ",
        elapsed_time,
    )
    print("---")
    print("SUCCESS")
