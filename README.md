# csimilarity

## Task Overview

This project, **csimilarity**, is designed to analyze and visualize the similarity between names. It converts names into mathematical vectors, calculates their similarity, stores these vectors in a database, and visualizes the relationships using a radar-style vector plot.

## 1. Improve Project Documentation

### Project Overview

This project converts names into mathematical vectors, calculates the similarity between names, and stores these vectors in a database. It then visualizes name similarity using a radar-style vector plot, showing which names are mathematically closer to each other. This allows for a clear, visual representation of how similar different names are based on their underlying characteristics.

### How It Works

#### Step 1 — Name → Vector

Each name is converted into a unique set of coordinates (X, Y) in a 2D vector space:

*   **X coordinate**: This is based on the **letter frequency patterns** within the name. Specifically, it is calculated as the sum of the squares of the frequencies of each letter (a-z) present in the name. For example, a name with many 'a's and 'b's will have a different X coordinate than a name with many 'x's and 'y's.

*   **Y coordinate**: This is based on the **letter positions and their alphabetical index**. It is calculated as the sum of (position of the letter in the name * alphabetical index of the letter). For instance, 'a' has an index of 1, 'b' is 2, and so on. A name where letters appear early in the alphabet and early in the name will have a different Y coordinate than a name with letters appearing later in the alphabet or later in the name.

#### Step 2 — Similarity Calculation

The similarity score between two names is primarily based on the **Euclidean distance** between their respective vectors in the 2D space. Names that are closer together in this vector space are considered more similar. The formula used to compute similarity is:

`Similarity = exp(-distance / scale)`

In simple terms, as the distance between two name vectors decreases, the similarity score increases exponentially. The `scale` factor (set to 50 in this project) adjusts the sensitivity of this relationship. Additionally, a component based on letter frequency similarity is included, contributing 30% to the overall score, while the vector distance contributes 70%.

#### Step 3 — Radar Plot Visualization

The radar plot provides a visual representation of name similarities:

*   **Radius (r)**: Represents the **vector magnitude**, which can be interpreted as the complexity or "heaviness" of the name. Longer vectors (larger radius) indicate more complex names.
*   **Angle (theta)**: Represents the **alphabetical composition** of the name. It indicates the "flavor" or "direction" of the name based on the average alphabetical index of its characters. For example, names starting with letters early in the alphabet might cluster in one angular section, while names with letters later in the alphabet might appear in another.
*   **Lines**: Represent **similarity connections** between names. Thicker and greener lines indicate higher similarity scores between the connected names.
*   **Nearby names**: Names that are plotted closer together on the radar chart are more similar.

### How To Read The Plot

*   **Names closer together**: Indicate higher similarity.
*   **Names far apart**: Indicate lower similarity.
*   **Lines**: Visually represent the similarity relationships between names. The intensity and thickness of the lines correspond to the similarity score.
*   **Longer vectors (larger radius)**: Suggest more complex names, often with a wider variety of letters or longer lengths.

### Features Section

*   **Vector Embedding of Names**: Converts names into numerical (x, y) coordinates.
*   **Similarity Scoring**: Calculates a quantitative similarity score between any two names.
*   **Radar Visualization**: Provides an intuitive graphical representation of name similarities.
*   **Database Caching of Vectors**: Stores calculated name vectors to optimize performance and avoid redundant computations.
*   **Interactive UI**: A user-friendly interface for inputting names and viewing results.
*   **Plot Generation**: Dynamically creates radar plots based on user input.

### Installation Instructions

To set up the project locally, follow these steps:

1.  Clone the repository:
    `git clone https://github.com/SOUGUR/csimilarity.git`
    `cd csimilarity`

2.  Install the required Python packages:
    `pip install -r requirements.txt`

3.  Apply database migrations:
    `python manage.py migrate`

4.  Run the development server:
    `python manage.py runserver`

### Deployment Instructions

This project is designed to be deployed on platforms like Render. Key considerations for deployment include:

*   **SQLite Database**: The project uses an SQLite database, which is suitable for smaller applications. For production environments, consider using a more robust database solution like PostgreSQL.
*   **Media Files for Plots**: Generated plots are saved as media files. On Render, these files need to be stored in a persistent disk to ensure they are not lost between deployments. The `MEDIA_ROOT` setting in `settings.py` should point to a writable persistent directory (e.g., `/var/data/media`).
*   **Gunicorn Server**: The application is served using Gunicorn in production, as specified in the `Procfile`.

## 2. Add Technical Explanation Section

### Mathematical Model

#### Vector Representation:

Each name `N` is transformed into a 2D vector `(x, y)` where:

*   `x = sum(letter_frequency²)`: The X-coordinate is the sum of the squares of the frequencies of each letter (a-z) in the name. This captures the overall distribution and prominence of letters.

*   `y = sum(position × alphabet_index)`: The Y-coordinate is the sum of the product of each letter's 1-based position in the name and its 1-based alphabetical index. This accounts for both the order and the alphabetical value of letters.

#### Similarity:

The similarity `S` between two names is calculated using a hybrid approach:

`S = 0.7 * exp(-distance(vector1, vector2) / scale) + 0.3 * letter_similarity(name1, name2)`

Where:

*   `distance(vector1, vector2)`: Is the Euclidean distance between the two name vectors.
*   `exp(-distance / scale)`: This term provides an exponential decay of similarity as the distance increases. The `scale` factor (50) controls the rate of decay.
*   `letter_similarity(name1, name2)`: This is a separate metric based on the difference in letter frequency distributions between the two names. It contributes 30% to the final similarity score, while the vector distance component contributes 70%.

## 3. Fix Plot Rendering Bug on Render

**Issue**: When deployed on Render, similarity calculations, database operations, and the UI function correctly, but generated plots are not visible, despite working locally.

**Investigation and Fix**: The primary cause of this issue is typically related to how media files (the generated plots) are handled in a production environment like Render. Render's ephemeral filesystem means that files written directly to the application directory are lost between deployments or restarts. The solution involves configuring Django to save media files to a **persistent disk** provided by Render and ensuring these files are served correctly in production.

**Specific Changes Made**:

*   **`settings.py`**: The `MEDIA_ROOT` setting was updated to point to a persistent directory on Render, specifically `/var/data/media`. An `os.makedirs` call was added to ensure this directory exists.
    ```python
    MEDIA_ROOT = os.path.join("/var/data", "media")
    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(MEDIA_ROOT)
    ```
*   **`Procfile`**: The `collectstatic` command was added to the `web` entry in the `Procfile` to ensure static files are collected during deployment. While `collectstatic` is for static files, ensuring proper static file serving can sometimes indirectly affect media file serving configurations or highlight other deployment issues.
    ```
    web: python manage.py collectstatic --noinput && gunicorn name_similarity.wsgi
    ```
*   **`name_similarity/urls.py`**: Modified to explicitly serve media files in production (when `DEBUG` is `False`) using `django.views.static.serve` with a `re_path` pattern. This ensures that URLs like `/media/plots/filename.png` are correctly mapped to the files stored in `MEDIA_ROOT`.
    ```python
    if not settings.DEBUG:
        from django.views.static import serve
        from django.urls import re_path

        urlpatterns += [
            re_path(r'^media/(?P<path>.*)$', serve, {
                'document_root': settings.MEDIA_ROOT,
            }),
        ]
    ```

**Explanation of the fix**: By directing `MEDIA_ROOT` to a persistent volume, the generated plot images will now persist across deployments. The updated `urls.py` ensures that these persisted media files are correctly served by Django itself when running in a production environment on Render, making them accessible via the configured `MEDIA_URL` (`/media/`). The `generate_plot()` function in `names/utils.py` already uses `settings.MEDIA_ROOT` to save the plots, so these changes ensure the plots are saved to the correct, persistent location and are also correctly exposed via a URL.

## 4. Fix Media Settings for Render

As detailed above, the `settings.py` file was updated to ensure `MEDIA_ROOT` points to a writable and persistent directory on Render. The `MEDIA_URL` remains `'/media/'`, and `name_similarity/urls.py` has been updated to correctly serve these media files in production.

## 5. Ensure Plot Generation Works on Render

The `generate_plot()` function in `names/utils.py` saves plots to `os.path.join(settings.MEDIA_ROOT, "plots")`. With the `MEDIA_ROOT` now correctly configured to a persistent path on Render, plots will be saved to `/var/data/media/plots/`. The function returns the path `media/plots/{filename}`, which, when combined with the updated `urls.py` configuration, forms the correct URL for accessing the image (e.g., `/media/plots/filename.png`). This ensures that plots are saved successfully, the folder exists, files persist, and file paths are correct for Render deployment.

## 6. Improve Project Clarity

Code comments and docstrings have been added to key functions in `names/utils.py` to improve understanding for beginners. This includes explanations for `alphabet_index`, `calculate_xy`, `get_or_create_vector`, `letter_similarity`, `distance`, `similarity_score`, and `generate_plot`. Variable names were already reasonably clear and did not require significant changes.

## 7. Deliverables

1.  **Updated `README.md`**: This document itself, providing a comprehensive overview, explanation of how the project works, mathematical model, and deployment details.
2.  **Updated headings and descriptions**: All relevant sections in the `README.md` have been updated to provide clear and beginner-friendly explanations.
3.  **Fixed `settings.py`**: `MEDIA_ROOT` configured for persistent storage on Render.
4.  **Fixed media configuration**: Ensured media files are saved to and served from the correct persistent location on Render.
5.  **Fixed plot rendering issue**: The combination of `settings.py`, `Procfile`, and `urls.py` changes addresses the plot visibility issue on Render.
6.  **Explanation of what was wrong with Render plot display**: Provided in section 3 of this `README.md`.
