#  ------------------------------------------------------------
#  Copyright (c) 2024 Rystal-Team
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#  ------------------------------------------------------------
#

import nextcord
from nextcord.ext import commands

from config.loader import bug_report_channel_id, default_lang, lang

class_namespace = "bug_class_title"


class BugReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description=lang[default_lang][class_namespace])
    async def bug(self, interaction: nextcord.Interaction):
        modal = BugReportModal(title="Bug Report")
        await interaction.response.send_modal(modal)


class BugReportModal(nextcord.ui.Modal):
    def __init__(self, title: str):
        super().__init__(title=title)
        self.add_item(
            nextcord.ui.TextInput(
                label="Bug Description",
                placeholder="Describe the bug...",
                style=nextcord.TextInputStyle.paragraph,
                min_length=1,
                max_length=500,
            )
        )
        self.add_item(
            nextcord.ui.TextInput(
                label="Steps to Reproduce",
                placeholder="List the steps to reproduce the bug...",
                style=nextcord.TextInputStyle.paragraph,
                min_length=1,
                max_length=500,
            )
        )
        self.add_item(
            nextcord.ui.TextInput(
                label="Expected Behavior",
                placeholder="What did you expect to happen...",
                style=nextcord.TextInputStyle.paragraph,
                min_length=1,
                max_length=500,
            )
        )

    async def callback(self, interaction: nextcord.Interaction):
        bug_description = self.children[0].value
        steps_to_reproduce = self.children[1].value
        expected_behavior = self.children[2].value

        bug_report_channel = interaction.guild.get_channel(bug_report_channel_id)
        if bug_report_channel:
            await bug_report_channel.send(
                f"**Bug Reported by {interaction.user.mention}[{interaction.user.global_name}]:**\n\n"
                f"**Description:** \n```{bug_description}```\n"
                f"**Steps to Reproduce:** \n```{steps_to_reproduce}```\n"
                f"**Expected Behavior:** \n```{expected_behavior}```"
            )

        await interaction.response.send_message(
            "Thank you for reporting the bug!", ephemeral=True
        )


def setup(bot):
    bot.add_cog(BugReport(bot))
