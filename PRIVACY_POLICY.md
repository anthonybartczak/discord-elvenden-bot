# Privacy Policy for Elvie Discord Bot

**Last Updated:** August 26, 2026

This Privacy Policy explains how **Elvie** ("the Bot", "we", "us", or "our"), an open-source Discord application helper for Warhammer Fantasy Roleplay 4th Edition (WFRP 4e), handles user data and privacy.

We are committed to respecting your privacy and protecting any information processed through our application in compliance with Discord's Developer Policy and applicable data protection regulations (such as GDPR).

---

## 1. Information We Process

Elvie is designed with privacy in mind and operates on a minimal-data approach. The Bot **does not** maintain any persistent database of personal user information, message histories, or server data.

When you interact with Elvie via Discord Slash Commands, the following data may be processed ephemerally:

- **Discord User IDs & Usernames:** Processed in volatile memory solely to attribute command responses (e.g., matching the user who clicked an interactive button in `/fortuna`).
- **Discord Guild (Server) IDs & Channel IDs:** Processed in volatile memory to deliver replies to the appropriate text channel and to calculate aggregate guild count via `/serwery`.
- **Command Inputs & Parameters:** Inputs provided in slash commands (e.g., `/rozwinięcie`, `/talent`, `/umiejętność`) are processed solely to calculate results or search reference tables.

### Data We DO NOT Collect or Store:
- ❌ We do **not** read, collect, or store private messages (DMs) or general server chat messages outside of direct slash command invocations.
- ❌ We do **not** collect passwords, email addresses, IP addresses, payment details, or personal sensitive information.
- ❌ We do **not** store any user data in external databases, third-party analytics services, or persistent storage files.
- ❌ We do **not** use tracking cookies or sell/share any user data with third-party advertisers or data brokers.

---

## 2. How We Use the Information

Any information received via the Discord API is used strictly for the following operational purposes:
- Executing requested slash commands (e.g., calculating WFRP 4e experience point costs, rolling tables for manifestations and corruption, looking up talents and skills).
- Managing interactive Discord UI components (buttons and autocomplete menus).
- Monitoring technical health, error troubleshooting, and real-time bot status via ephemeral standard runtime console logs.

---

## 3. Data Storage, Retention, and Deletion

- **Ephemeral Processing:** All command inputs, interaction tokens, and Discord identifiers are processed in memory and are discarded immediately after the command execution is completed or timed out.
- **Data Retention:** Because Elvie does not store persistent user data, there is no permanent data retention.
- **Data Deletion:** Since no identifiable user data is stored on disk or in databases, there is no personal data to delete. Removing the bot from your Discord server immediately terminates any interaction with that server.

If you have questions regarding data processing or wish to verify data handling, you may reach out via the contact methods listed below.

---

## 4. Third-Party Services

Elvie relies on the **Discord API** to provide its services. By using Elvie, you also acknowledge and agree to Discord's policies:
- [Discord Terms of Service](https://discord.com/terms)
- [Discord Privacy Policy](https://discord.com/privacy)

Elvie does not send your data to any other third-party servers, analytics providers, or external processing endpoints.

---

## 5. Children's Privacy

Elvie complies with Discord's Terms of Service and does not knowingly collect or solicit personal data from children under the minimum age required by Discord (13 years of age, or higher depending on local jurisdiction laws).

---

## 6. Changes to This Privacy Policy

We reserve the right to update this Privacy Policy at any time to reflect changes in functionality, legal requirements, or Discord platform policies. Any modifications will be posted directly to this repository with an updated revision date.

---

## 7. Contact Us

If you have any questions, concerns, or requests regarding this Privacy Policy or Elvie's operation, please contact us by:
- Opening an issue on GitHub: [https://github.com/anthonybartczak/discord-elvenden-bot/issues](https://github.com/anthonybartczak/discord-elvenden-bot/issues)
- Developer Profile: [anthonybartczak](https://github.com/anthonybartczak)
