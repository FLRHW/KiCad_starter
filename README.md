# FLRHW KiCad Starter

A KiCad 10 project template with hierarchical schematic examples, drawing
worksheets, and GitHub Actions automation using KiBot.

Start a project in KiCad, develop the design, and push changes to GitHub. CI
generates documentation and manufacturing files and commits them back to the
same branch. Retrieve the results with `git pull`.

Repository: [FLRHW/KiCad_starter](https://github.com/FLRHW/KiCad_starter).

## Requirements

- KiCad 10 installed locally, with its standard symbol and footprint libraries.
- Python 3 to run the project setup and optional local utilities.
- Git and a GitHub account for the CI workflow.
- A browser and PDF viewer to inspect generated documents.

Docker and KiBot do not need to be installed locally. The workflow runs them on
a GitHub-hosted Ubuntu runner. Local KiCad and CI KiCad patch versions can differ;
the CI build report records the version that generated the outputs.

**Platform testing:** This template has been tested only on Linux. Local project
creation and setup are expected to work on Windows with KiCad 10, Python 3 and Git,
but have not yet been verified there. The CI workflow runs on Ubuntu regardless
of the operating system used locally. Shell examples below use Linux syntax unless
stated otherwise.

## Included outputs

Depending on the configuration toggles, CI generates:

- ERC and DRC reports, including machine-readable JSON.
- Schematic PDF.
- Fabrication PDF with requirements, stackup and drill documentation.
- Assembly PDF with drawings, component counts and paginated BOM appendices.
- Separate top/bottom testpoint drawing pages.
- Gerber and Excellon drill files.
- CSV and XLSX BOMs and an interactive HTML BOM.
- Top/bottom pick-and-place CSV files.
- A STEP assembly and optional Blender renders, including bare-board views.
- An HTML index linking the generated outputs.
- Optional fabrication/assembly ZIP packages and revision comparison PDFs.

## Install the KiCad template

1. Clone or download this repository into a folder under your user template
   directory. For example, on Linux:

   ```bash
   mkdir -p "$HOME/KiCadTemplates"
   git clone https://github.com/FLRHW/KiCad_starter.git "$HOME/KiCadTemplates/KiCad_starter"
   ```

2. In the KiCad Project Manager, open **Preferences → Configure Paths** and set
   `KICAD_USER_TEMPLATE_DIR` to the parent folder, such as
   `/home/your-user/KiCadTemplates`. Leave the system template path unchanged.

3. Choose **File → New Project…** and select **FLRHW KiCad Starter**.

4. Choose the new project name and location. KiCad renames the root project,
   schematic, PCB and rules files; the example child-sheet filenames remain
   unchanged.

`meta/info.html` and `meta/icon.png` provide the template description and icon.
The `templates/` folder contains drawing worksheets; it is a different folder
from the directory used to install project templates.

## Set up a newly created project

Before opening the new project's schematic or PCB editors, open a terminal in
its root folder and run:

```bash
python3 scripts/setup_project.py
```

On Windows, `py scripts/setup_project.py` may be used instead.

The setup script updates internal project-name records and installs the workflow
from `ci/workflows/` into `.github/workflows/`. This is required because KiCad
does not copy the hidden `.github/` folder when creating a project from a template.
Running setup again is safe when the files already match. It refuses to overwrite
a different existing workflow unless you explicitly use `--force`.

Then open the new `.kicad_pro` file, check the hierarchy, save the design and run
local ERC/DRC. The example hierarchy includes a cover page, system overview,
block diagram, interface example and two circuit examples. Adapt or delete the
examples through KiCad before removing their unused files from disk.

The workflow expects exactly one `.kicad_pcb` in the project root and a matching
root `.kicad_sch`. Hierarchical child sheets are supported.

## Connect the project to GitHub

Create an empty GitHub repository without adding another README, licence or
`.gitignore`. From the new project's root:

```bash
git init -b main
git remote add origin git@github.com:YOUR_ACCOUNT/YOUR_REPOSITORY.git
git add .
git commit -m "Create project from FLRHW KiCad Starter"
git push -u origin main
```

Replace the remote with your repository address.
If Actions is disabled for the repository, enable it. Repository or organisation
policies must permit the workflow's `contents: write` permission so CI can commit
generated outputs.

After a successful run:

```bash
git pull --ff-only
```

CI adds commits to the branch you pushed. Pull those commits before starting the
next edit. If a push is rejected because CI has added a commit and your local
changes are already committed, integrate it with `git pull --rebase`, resolve any
conflicts, and then push. Do not force-push over CI's output commits.

## Project settings and worksheets

- Set your project name, revision, company and issue date in the appropriate
  KiCad page settings and project text variables.
- Enter dates as `YYYY-MM-DD`; KiBot formats them for the documents.
- The BOM configuration reads **Manufacturer** and **Manufacturer Part Number**.
  Its displayed part-number column may be labelled **MPN**.
- Use KiCad's **Do not populate** flag for unfitted parts. Check BOM and
  pick-and-place filtering for your assembly requirements.
- Select the appropriate worksheet under `templates/` in schematic and PCB page
  settings. Board worksheets are supplied for A2/A3/A4/A5; schematic worksheets
  are supplied for A3/A4.
- CI updates the `SHEET_TITLE_n` text variables used by the contents page. The
  workflow commits the project file so these generated values can be pulled and
  displayed locally. Local values may remain stale until that update.

The supplied design rules, dimensions and fabrication notes are merely illustrative.
Set them to your board manufacturer's requirements and inspect the generated files
before ordering or assembling boards.

## Configuration toggles

Edit the `definitions:` document at the end of `config.kibot.yaml`:

| Setting | Values | Behaviour |
|---|---|---|
| `RENDER_MODE` | `disabled`, `low`, `mid`, `high` | Controls Blender rendering and image layers in drawings. |
| `ASSEMBLY_BOM_MODE` | `combined`, `fitted`, `separate`, `no bom` | Selects the assembly PDF's BOM appendices. |
| `ZIP_ENABLED` | `'true'`, `'false'` | Enables or disables manufacturing ZIP packages. |
| `DIFF_ENABLED` | `'true'`, `'false'` | Enables or disables revision comparisons. |
| `DIFF_BASE_REF` | Git commit or tag | Reference revision for comparisons. |

In `combined` mode, fitted and DNP parts share a table with a Status column.
`fitted` includes fitted parts only. `separate` creates distinct fitted and DNP
sections. Both omit Status because their section headings identify the population.
`no bom` omits the appendices. Source CSVs retain Status for classification.

Disabling renders leaves the PDF pages in place, with render areas blank and
associated image layers omitted. Higher render modes cost more CI time.

Several values use KiBot's `@DEFINITION@` substitution syntax. Keep the supplied
multi-document configuration structure; a generic YAML parser alone does not
perform these substitutions.

### Blender lighting

Define lights in `config.kibot.yaml`. The Blender hook in
`scripts/configure_blender_materials.py` then adjusts every AREA light,
including any additional ones you define.

The hook measures the rendered board and components, preserves each light's
direction from their centre, and aims the light toward that centre. It sets
the distance to six times the measured board size and the softbox width and
height to four times that size.

Consequently, moving a light farther along the same direction in the YAML
does not reduce its brightness: the script overrides that distance.

Light energy is handled separately:
- `energy: @AUTO_LIGHT_ENERGY@` uses board-size compensation calculated by
  the workflow.
- A numeric energy value remains fixed.
- Arithmetic expressions are not supported in the numeric energy field.

The distance and size adjustments apply to AREA lights, not SUN lights.
The current hook requires at least one AREA light when rendering is enabled.
It also adjusts materials and colour settings, so the final appearance is
controlled by both the YAML and the hook.

Use `RENDER_MODE` to disable rendering or select its quality. The hook is
designed for the pinned CI image; changing the KiBot or Blender version may
require checking its compatibility.

### Workflow dependencies and output selection

Use the supplied render, assembly BOM, ZIP and revision-comparison toggles
where possible. These are supported configuration paths; other outputs
cannot necessarily be removed or disabled independently.

Before changing an output's name, path or enabled state, check its references
in:
- `config.kibot.yaml`, including PDF images, tables and package definitions.
- The workflow's output-selection and exclusion lists.
- The helper scripts, especially `finalize_pdfs.py`.

Setting `run_by_default: false` only disables default execution. An output
may still be requested explicitly by another output or script. Removing its
definition can invalidate those requests and cause CI to fail.

Important dependencies:
- PDF finalisation requires the assembly PDF and both ERC/DRC JSON reports.
- Unless `ASSEMBLY_BOM_MODE` is `no bom`, it also requires the top and bottom
  assembly BOM CSVs under `output/tables/`. Keep their configured columns,
  including Status, even when Status is omitted from the PDF.
- The assembly cover-page iBOM link requires the generated iBOM HTML.
  Its current implementation expects an unmirrored first page at 1:1 scale
  and the named `assembly_ibom_link` group.
- ERC failures require the schematic PDF for its failure notice. DRC failures
  require the assembly and fabrication PDFs.
- Drawing tables, render placeholders and ZIP packages depend on their
  referenced outputs or files.

The workflow can fail before PDF finalisation—for example, when a required
configuration file is missing, project-file detection fails, a helper command
fails, or KiBot cannot resolve a referenced output. Its shell uses `set -e`,
so an unsuccessful command normally stops the current step.

Preserve the execution order: generate fresh outputs, finalise the PDFs,
then generate packages and the HTML index. Do not repeatedly finalise an
already-finalised assembly PDF.

Disabling generation does not delete previously committed outputs. Older
files may remain available to scripts or links, so their presence does not
prove they were regenerated.

`pdf_mask_colours.py` reads physical solder-mask colours from the PCB stackup,
not the editor display theme. Missing or unsupported colours use its fallback.

Run `setup_project.py` locally after template creation. Rendering and PDF
processing run inside the CI container; ordinary local Python does not
provide all their required dependencies.

## PCB document layers and placeholders

The PDF outputs use custom layers and named groups. Preserve them when clearing
the example PCB, and adapt their placement to the board and paper size.

| Layer | Purpose |
|---|---|
| `AssemblyOverview` | Assembly cover-page renders and related annotations. |
| `AssemblyTop`, `AssemblyBottom` | Side-specific render/table placeholders. |
| `AssyDNPTop`, `AssyDNPBottom` | Generated DNP markings. |
| `FabricationRender` | Bare-board render placeholders. |
| `FabricationNotes` | Requirements text and stackup drawing. |
| `FabricationDrillMap` | Generated drill drawings. |
| `TestpointsTop`, `TestpointsBottom` | Testpoint annotations. |

Image groups use KiBot's `kibot_image_...` conventions; table groups use the
configured table names. Keep the existing names aligned with the YAML and scripts.
For bottom testpoint labels, verify text orientation in KiCad's flipped view and
check the page's `mirror_pcb_text` setting. Testpoint filtering currently recognises
references in the form `TP` followed by digits.

Most supplied PCB drawing pages use an explicit 1:1 scale. A larger worksheet does
not automatically resize the drawing; change the page scaling and its displayed
scale label together when needed.

## Output locations and viewing

| Location | Contents |
|---|---|
| `output/` | Schematic PDF and root HTML index link. |
| `output/assembly/` | Assembly and testpoint PDFs, BOM/iBOM and placement files. |
| `output/fabrication/` | Fabrication PDF, Gerbers and drill files. |
| `output/3d/` | STEP model and enabled renders. |
| `output/tables/` | Auxiliary CSV tables used by the documents. |
| `output/reports/` | ERC/DRC reports, check status, build information and HTML navigation. |
| `output/packages/` | Enabled manufacturing ZIPs. |

Generated outputs are intentionally tracked in project repositories. Keep
`output/` out of their `.gitignore`. Remove generated outputs from the starter
before distributing it or creating new projects.

Open `output/index.html` to browse generated files.

The standalone iBOM can normally be opened directly. Relative links from PDFs
depend on preserving the output folder layout and the PDF viewer's support for
opening local links.

ERC errors mark the schematic PDF; DRC errors mark the assembly and fabrication
PDFs. The workflow can continue generating documents after those design-check
errors. A green workflow therefore does not establish that the design checks passed:
inspect `output/reports/check-status.txt` and the ERC/DRC reports.

## Libraries, fonts and reproducibility

The starter uses standard KiCad libraries. Project-specific registrations with the
same nickname override global libraries, so avoid activating a partial snapshot while
you still need access to the complete installed library.

`scripts/clone_libs.py --help` describes the optional library snapshot utility.
For production projects, retain the required libraries and 3D models locally and
review the resulting library tables. Project-local models can be stored under
`lib/3D/` and referenced with `${KIPRJMOD}/lib/3D/...`.

Use fonts available in CI, such as DejaVu Sans, or explicitly provide suitable font
resources. Selecting a default font does not change text objects that explicitly
request another font. CI preferences and colours are stored under `ci/kicad/`.

The workflow pins its Docker image by digest and GitHub Actions by commit. The
tested image is mirrored under `ghcr.io/flrhw/kibot-kicad10`; preservation tooling
is maintained in [kicad10_ci_tools](https://github.com/FLRHW/kicad10_ci_tools).
The build report records the source commit, CI image and tool versions.

The hosted runner and missing-model downloads are separate dependencies.
A pinned digest fixes image contents but does not guarantee
that a registry will retain them forever. Keep a verified image archive outside the
registry for long-term recovery. Review external resources before freezing a release.

## Maintaining the template

- When maintaining the starter, edit `ci/workflows/kicad-environment.yml`, the
  workflow copy that KiCad includes in new projects. Then run
  `python3 scripts/setup_project.py --force` to update the active copy under
  `.github/workflows/`, and commit both files. GitHub executes the active copy.
  In a project created from the template, you can edit its active workflow
  directly; changes there do not update the starter or other projects.
- Keep both workflow exclusion lists in sync when adding outputs. Main outputs
  run before PDF finalisation; packages and the HTML index run afterwards.
- Changes to scripts, worksheets and YAML affect the template and future projects.
  Existing projects do not automatically inherit updates.
- Validate changes by creating a project with a different name and checking local
  ERC/DRC, CI, generated PDFs, links and output paths.
- Update this README when configuration names, paths or requirements change.
- In a generated project, replace this README with project documentation or move
  it to a retained template-usage guide.

## Licence

The original FLRHW KiCad Starter material—including its scripts, configuration,
worksheets, documentation and original example designs—is licensed under the
**MIT License**. See [LICENSE](LICENSE). Preserve the copyright and permission
notice when distributing copies or substantial portions of this material.

Using this template does not require your independently created hardware design
to use MIT. Choose and document the licence appropriate for your project. If you
replace a generated project's root licence, retain the template's MIT notice in a
clearly identified location, for example `LICENSES/FLRHW-KiCad-Starter-MIT.txt`, and
state which reused material it covers.

Third-party software, libraries, models, fonts and other incorporated material
retain their respective licences. The template's MIT licence does not relicense
them. Preserve applicable third-party copyright and licence notices, including
those accompanying generated outputs that contain third-party code, such as iBOM.

All product names and trademarks belong to their respective owners. References
are descriptive and do not imply endorsement or affiliation. The template is
provided as is, without warranty, under the terms of LICENSE.

## Credits and acknowledgements

Development of this template was AI assisted, including work on configuration, 
helper scripts, documentation and troubleshooting. Project decisions and testing 
were carried out by FLRHW.

This template relies on the work of many open-source contributors:

- [KiBot](https://github.com/INTI-CMNB/KiBot), developed by Salvador E. Tropea,
  INTI and contributors, building on work including John Beard's KiPlot:
  automation, reports, exports and document generation.
- [KDT_Hierarchical_KiBot](https://github.com/nguyen-v/KDT_Hierarchical_KiBot),
  by Vincent Nguyen: inspiration for project organisation and automated
  documentation.
- [KiCad](https://www.kicad.org/) and its library contributors: schematic/PCB
  editing, checks, plotting and 3D export.
- [KiAuto](https://github.com/INTI-CMNB/KiAuto): KiCad automation utilities.
- [InteractiveHtmlBom](https://github.com/openscopeproject/InteractiveHtmlBom),
  by qu1ck and contributors: interactive assembly BOM.
- [Blender](https://www.blender.org/) and
  [PCB2Blender](https://github.com/30350n/pcb2blender): board rendering.
- [GitHub Actions](https://github.com/features/actions) and its action authors:
  CI execution, checkout and artifact handling.

