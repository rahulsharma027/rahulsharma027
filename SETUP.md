# GitHub profile draft

Prepared for [rahulsharma027](https://github.com/rahulsharma027) on 26 October 2026.

## Publish the draft

Your public profile repository already exists at [rahulsharma027/rahulsharma027](https://github.com/rahulsharma027/rahulsharma027). Its current README contains only a newline.

1. Replace that repository's root `README.md` with the `README.md` in this folder.
2. Upload the complete `assets/`, `scripts/`, and `.github/` directories from this folder, preserving their paths. The hidden `.github/` directory contains the refresh workflow.
3. Preview the README on GitHub, then commit the files. GitHub will display the README on your profile.
4. On your profile, choose **Customize your pins** and feature the four projects listed below.
5. In the profile repository's **Actions** tab, enable workflows if prompted. Open **Refresh profile widgets** and choose **Run workflow** for its first hosted run.

The files in this folder are a local draft. They have not been uploaded to GitHub.

## Suggested profile details

- **Name:** Rahul Sharma
- **Bio:** Software engineer | Go, Java & API platforms | Kubernetes, cloud & observability | Previously Cisco (contract) | Open to opportunities
- **Location:** Bengaluru, India (already set)
- **LinkedIn:** https://www.linkedin.com/in/rahul-sharma-6931b914b/
- **Email:** rahulsharma84244@gmail.com
- **Website:** Add your portfolio when ready.

## Included widgets

- **Engineering impact:** Three static highlights from your resume: 40% latency reduction, 1,000+ developer accounts synchronized, and GraphQL publishing across four services.
- **Technology loadout:** Twelve locally embedded logos. Their source files and license notice are included under `assets/`.
- **GitHub public inventory:** Public repository count, non-fork repository count, and number of detected code languages.
- **Language distribution:** Code-byte share across owned public repositories, excluding forks. This is not a proficiency score and does not capture your professional work in private repositories.
- **Recent builds:** Four most recently pushed public projects, excluding forks, archived repositories, and the profile repository.

Every image has a separate mobile layout selected through `<picture>`. All images are stored in your profile repository, so displaying them does not depend on a third-party stats service.

### Automatic refresh

`.github/workflows/profile-widgets.yml` regenerates the three public GitHub widgets weekly on Monday at 04:23 UTC (09:53 IST). It also supports manual runs and runs when its script or workflow is changed on `main`.

It uses the repository's built-in `GITHUB_TOKEN`; no personal access token or separate backend is needed. `contents: write` allows the workflow to commit the six desktop/mobile widget files to this profile repository. Repository or organization policies and branch protection may need to allow this bot commit. It makes no changes to other repositories.

The hosted workflow has not been run from this local draft. The widgets already contain a real public API snapshot from 26 October 2026. If a future API request fails, the script exits with an error before replacing the existing cards.

To refresh locally with Python 3.10 or newer:

```bash
python scripts/update_widgets.py --username rahulsharma027
```

To rebuild the technology strip using the included logo files:

```bash
python scripts/build_tech_loadout.py
```

## Resume-based content

The October resume supplied for this task is the source for the Cisco contractual role, employment dates, production work, Revature internship, impact figures, education, certifications, LinkedIn, and email. Your public repositories supply the project links and robotics story.

The 99.9% figure is described as an uptime SLA, rather than a measured uptime result. Leadership principles are presented as working habits supported by examples, with no claim of a management title. Professional projects are described in the experience section; their private source code is not represented as a public repository.

## Recommended project pins

Based on the public READMEs and file lists, these make the clearest initial selection:

1. [movie-booking-system-capstone](https://github.com/rahulsharma027/movie-booking-system-capstone): the strongest candidate for Java and web roles. The file tree includes a Spring Boot backend, Angular frontend, Dockerfiles, Compose, and Jenkins configuration.
2. [AI-Image-Generation-App](https://github.com/rahulsharma027/AI-Image-Generation-App): the README records your team-lead role and provides a video demonstration. The source tree includes React components and a Python API.
3. [Maze-Solving-Robot](https://github.com/rahulsharma027/Maze-Solving-Robot): gives the profile a distinctive personal story, with Arduino code and a demonstration video.
4. [Movie-Recommender-System](https://github.com/rahulsharma027/Movie-Recommender-System): shows a separate Python project; its README describes Streamlit and cosine similarity.

This selection is based on documentation and repository structure, not a runtime check or complete source review.

## Improvements worth making next

- Add one-sentence repository descriptions. Of the 21 public repositories returned by GitHub's API, 18 had no description when reviewed.
- Choose one movie-booking repository to feature. `capstone-project` and `movie-booking-system-capstone` describe the same application; the latter has the more recent push and expanded admin UI. Confirm that it is your preferred version.
- Choose one image-generation repository to feature. There are several similarly named versions; the draft uses `AI-Image-Generation-App` because it explains the project and your role most clearly.
- Update featured project READMEs with a short overview, your contribution, a few screenshots, setup instructions, and implementation status.
- Replace template text such as `yourusername`, `Your Name`, and `your.email@example.com` in the capstone documentation. Keep planned payment and email features clearly labelled as planned.
- Check old demo URLs before adding them to the profile. The image-generation README already mentions limitations in its hosted demo, so the draft links to the repository instead.
- Add a portfolio link once the site is ready; email and LinkedIn are already included in the draft.

## Optional details for a future revision

- A more specific target role if you want to narrow the current backend, API, and cloud focus.
- Any favourite games or visual references you want reflected in the design.

The current banner uses the maze-solving project as its visual reference. Professional impact figures come from the supplied resume, and public code charts are labelled separately.
