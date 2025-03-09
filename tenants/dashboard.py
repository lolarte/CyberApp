from django.utils.translation import gettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard
from jet.dashboard.modules import ModelList, AppList
import logging

logger = logging.getLogger(__name__)

class CustomIndexDashboard(Dashboard):
    """
    Custom dashboard for Django JET Reboot.
    Renames sections such as "MAILTEMPLATES" to "Mail Simulations".
    """

    def init_with_context(self, context):
        logger.info("🚀 Django JET Dashboard is loading CustomIndexDashboard!")

        # ✅ Administration Section
        self.children.append(ModelList(
            title="Administration",
            models=[
                "accounts.CustomUser",  
                "auth.Group",
            ],
        ))

        # ✅ Renamed Applications Section
        self.children.append(ModelList(
            title="Campaigns",  # ✅ Renamed from "CAMPAIGNS"
            models=[
                "campaigns.Campaign",
                "campaigns.PhishingTestLog",
            ],
        ))

        # ✅ Mail Simulations (WITHOUT SUBSECTIONS)
        self.children.append(ModelList(
            title="Email Simulations",  # ✅ Renamed from "MAILTEMPLATES"
            models=[
                "mailtemplates.EmailTemplate",  # ✅ Directly listed models
            ],
        ))

        logger.info("✅ Django JET Dashboard has been updated!")
        print("✅ Custom Dashboard Updated!") 