# AGENTS.md

## General Guidelines:
- Code should be easy to read and understand.
- Keep the code simple. Avoid unnecessary complexity.
- Use meaningful names for variables, functions, etc. Names should reveal intent.
- Functions should be small and do one thing well.
- Common/repeated code should be extracted to a function.
- Function names should describe the action being performed.
- Use `snake_case` for function and variable names, avoid `CamelCase`.
- Only use comments when necessary, as they can become outdated.
  Instead, strive to make the code self-explanatory.
- When comments are used, they should add useful information that is not
  readily apparent from the code itself.

## Javascript Guidelines:
- Avoid embedded/anonymous functions if they are more than few lines;
  instead, extract the code to a named function and use it.
- Prefer `let` , avoid `var` when possible.
- initialization code ("on DOM ready") should be done from a function
  (typically called `setup()`).

## Python Guidelines:
- When catching exceptions, NEVER catch the generic `exception` class;
  instead, catch specific exception classes that are relevant to the code and possible errors.
- With exceptions, prefer concise code and let exceptions propegate instead of catching
  minor ones (like `KeyError`) unless critical to the logic of the code.

## Python/Flask Guidelines:
- Don't catch minor/redudent exceptions unless critical to the logic of the code.
- Let exceptions propagate and be handleded by Flask.
- Do not use `db.session.rollback()` on exceptions - this happens automatically with Flask.

## HTML/Jinja Guidelines:
- Use `bootstrap5` CSS classes as much as possible.
- Assume bootstrap5 and JQuery are already loaded (in `layout.html`).
- Jinja2 should be used primarily for rendering, not for logic/preprocessing.
  move preprocesssing to python backend (or even better - to DB/SQL).
- UI/UX:
  - top proirity is desktop laptop with Google-Chrome (or ChromeOS) .
  - The website MUST be useable on screen resolution 1024x768.
    - Vertical scrolling is good.
    - Horizontal scrolling is not good.
  - Do not use "skeleton screns"/"lazy loading". HTML Pages should be rendered
    on server-side (with Jinja) as much as possible.

## Git
- Each commit should contain one logical feature/bugfix/change.
- Avoid combining unrelated changes into one git commit.
- The first line in the git commit message should have a prefix
  explaning the domain/top-level component, e.g.:
   `maint:`, `doc:`, `DB:` `HTML:`, `admin:` (for flask-admin),
   `scripts:` (for shell/bat files),  or other higher-level components.
  Follow the prefix with short description.
-  The first line should ideally be less than 75 characeters.
-  Add additional information in following lines in the git message.
-  Add a blank line between the first git commit message and the rest.

