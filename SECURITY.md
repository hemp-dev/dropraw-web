# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| 0.1.x | Security fixes where practical |

## Reporting Vulnerabilities

Please report vulnerabilities privately to `GitHub Security Advisories` until the project maintainers publish a dedicated security contact.

Do not include secrets, tokens, credentials, private links, or real customer data in public issues.

## Token Safety

Never log, commit, paste into issues, or include in reports:

- Dropbox tokens.
- Dropbox shared-link passwords.
- Google credentials.
- OAuth refresh tokens.
- AWS access keys or secret keys.
- Git hosting tokens.
- CI/CD secrets.

## Metadata Privacy

The recommended default for public websites is metadata mode `strip`. It removes GPS and private camera data where the output encoder supports it. `keep-color` may preserve color information while still removing private metadata where possible.

## Logs And Reports

Logs and generated reports must not include credentials. File paths may be present, so avoid sharing private directory names publicly if that matters for your workflow.

## Mirrors And CI

International and Russian mirrors must not store secrets in the repository. Mirror scripts use remote names only and do not include credentials.

Configure tokens only in platform secret stores such as GitHub Actions secrets, GitLab CI variables, Bitbucket repository variables, or the equivalent private storage in self-hosted systems.
