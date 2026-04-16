# CLAUDE.md — Products.MeetingMons

## What is this project?

Products.MeetingMons is a **PloneMeeting extension profile** for the city of Mons (Belgium). It customizes the meeting management system for Mons's College and Council with a multi-level validation workflow, budget impact review, and Mons-specific document generation templates.

It sits in a three-layer inheritance chain:

```
Products.PloneMeeting          (base deliberation engine)
  └─ Products.MeetingCommunes  (communes common profile)
       └─ Products.MeetingMons (Mons-specific customizations)
```

All adapters, test cases, and browser views inherit from **MeetingCommunes**, not directly from PloneMeeting.

## Tech stack

- **Python 2.7** on **Plone 4.3** (Zope 2)
- Build system: **zc.buildout** (extends `communes-dev.cfg` from `buildout.pm`)
- Content types: Archetypes (MeetingItem, MeetingConfig) + Dexterity (Meeting, advices, annexes)
- Document generation: **collective.documentgenerator** / **appy** (POD templates)
- CI: GitHub Actions (self-hosted runner `gha-runners-delib-py2`)

See `Products.PloneMeeting/CLAUDE.md` for full tech stack details.

## Repository layout

```
Products.MeetingMons/
  setup.py                  # Package metadata (version in 'version' variable)
  buildout.cfg              # Extends communes-dev.cfg, defines testmons runner
  CHANGES.rst               # Changelog (update for every user-facing change)
  src/Products/MeetingMons/
    __init__.py             # Package init, registers skins, imports model/adapters
    config.py               # Constants: group suffixes, validation levels, finance config
    interfaces.py           # Zope interfaces for WF conditions/actions + browser layer
    adapters.py             # Core logic: custom adapters for Meeting, Item, Config, Tool
    setuphandlers.py        # GenericSetup install handlers
    testing.py              # Test layer (MM_TESTING_PROFILE_FUNCTIONAL)
    browser/
      configure.zcml        # View registrations
      overrides.py          # Document generation helpers, assembly formatting
      views.py              # Advice WF conditions view, group users display
    model/
      pm_updates.py         # Schema extensions (initItemDecisionIfEmptyOnDecide, validateByBudget)
    profiles/
      default/              # GenericSetup profile (version 4200) — workflows, skins, CSS/JS
      mons/                 # Production instance data (orgs, users, meeting configs)
      testing/              # Test profile with sample data
    migrations/             # Version-specific upgrade steps
    skins/                  # Plone skin layers (images, styles, templates)
    tests/                  # Test suite (23 test modules)
    locales/                # French translations
```

## Key customizations over MeetingCommunes

### Multi-level item validation workflow

Defined in `config.py` as `MONS_ITEM_WF_VALIDATION_LEVELS` — items go through 5 states:

1. `itemcreated` (creators)
2. `proposed_to_servicehead` (serviceheads)
3. `proposed_to_officemanager` (officemanagers)
4. `proposed_to_divisionhead` (divisionheads)
5. `proposed_to_director` (reviewers)

### Extra group suffixes

Mons adds 5 custom organization suffixes (set in `config.py` via `PMconfig.EXTRA_GROUP_SUFFIXES`):
`divisionheads`, `officemanagers`, `serviceheads`, `extraordinarybudget`, `budgetimpactreviewers`

### Budget impact review

The `mons_budget_reviewer` workflow adaptation (custom WFA in `adapters.py:CustomToolPloneMeeting.performCustomWFAdaptations`) adds two isolated states branching from `itemcreated`:
- `proposed_to_budgetimpact_reviewer`
- `proposed_to_extraordinarybudget`

Budget validation is enforced: items with `budgetRelated=True` cannot advance to servicehead without `validateByBudget` being set (see `MeetingItemCollegeMonsWorkflowConditions`).

### Document generation

`browser/overrides.py` provides Mons-specific printing methods:
- `printFinanceAdvice()` — handles legal, simple, initiative, and not-given finance advice cases
- `printFormatedItemAssembly()` / `printFormatedMeetingAssembly()` — assembly formatting
- `get_grouped_items()` / `get_multiple_level_printing()` — hierarchical item grouping for document templates

## Building & running

From the buildout root (`pm42_dev/`):

```bash
bin/buildout              # Build/install
bin/instance fg           # Run Plone in foreground
```

## Running tests

Tests require LibreOffice running for document conversion:

```bash
# Start LibreOffice (in background)
soffice '--accept=socket,host=0.0.0.0,port=2002;urp;StarOffice.ServiceManager' --nologo --headless --nofirststartwizard --norestore &

# Run all tests (from buildout root)
OO_SERVER=localhost OO_PORT=2002 bin/testmons --layer=\!ROBOT --test=\!\(testSetup\|testPerf\)

# Run a single test module
OO_SERVER=localhost OO_PORT=2002 bin/testmons -t testCustomWorkflows

# Run a single test method
OO_SERVER=localhost OO_PORT=2002 bin/testmons -t test_method_name
```

Test base class: `MeetingMonsTestCase` (inherits from `MeetingCommunesTestCase` + `MeetingMonsTestingHelpers`). Test layer: `MM_TESTING_PROFILE_FUNCTIONAL`. Some test files are inherited from parent packages and skipped via `subproductIgnoredTestFiles`.

## Code style & conventions

Follow the same conventions as Products.PloneMeeting (see its CLAUDE.md):

- `# -*- coding: utf-8 -*-` encoding header on every `.py` file
- GPL license header
- `AccessControl.ClassSecurityInfo` + `InitializeClass` for security declarations
- i18n: `from Products.PloneMeeting.config import PMMessageFactory as _`
- Single-line imports, alphabetically sorted

## Adapter pattern

All customization is done through **Zope adapters**, not class inheritance on content types:

| Adapter class | Adapts | Inherits from |
|---------------|--------|---------------|
| `CustomMeeting` | IMeeting -> IMeetingCustom | `MCMeeting` (Communes) |
| `CustomMeetingItem` | IMeetingItem -> IMeetingItemCustom | `MCMeetingItem` |
| `CustomMeetingConfig` | IMeetingConfig -> IMeetingConfigCustom | `MCMeetingConfig` |
| `CustomToolPloneMeeting` | ToolPloneMeeting -> IToolPloneMeetingCustom | `MCToolPloneMeeting` |
| `MeetingCollegeMonsWorkflowActions` | workflow actions | `MeetingCommunesWorkflowActions` |
| `MeetingCollegeMonsWorkflowConditions` | workflow conditions | `MeetingCommunesWorkflowConditions` |
| `MeetingItemCollegeMonsWorkflowActions` | item WF actions | `MeetingItemCommunesWorkflowActions` |
| `MeetingItemCollegeMonsWorkflowConditions` | item WF conditions | `MeetingItemCommunesWorkflowConditions` |
| `MMItemPrettyLinkAdapter` | item pretty links | `ItemPrettyLinkAdapter` |

Adapters are registered in `overrides.zcml` and initialized with `InitializeClass()` at the bottom of `adapters.py`.

## Workflow adaptations

The full list of active WF adaptations is defined in `adapters.py` as `customWfAdaptations` and assigned to `MeetingConfig.wfAdaptations`. The only Mons-specific WFA is `mons_budget_reviewer`; the rest come from PloneMeeting/Communes.

## Commit message style

Short imperative sentence. See `CHANGES.rst` for format:

```rst
- Description of change with `backtick-quoted` references.
  [author_shortname]
```

## Versioning

- Version string is in `setup.py` (`version = '...'`)
- GenericSetup profile version is in `profiles/default/metadata.xml`
- Development versions use `.dev0` suffix
