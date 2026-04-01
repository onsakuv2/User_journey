User Journey: Adding a "Country" Field to the Task Page
Alright Sam, let me paint you a picture...

The Story
Imagine Sam, our trusty task manager user, sitting at their desk. They're coordinating work across multiple regions — a vendor meeting in Germany, a compliance deadline in Brazil, a product launch in Japan. They open their task manager, start creating a new task, and... there's no way to capture where this task lives geographically. The context is lost. They resort to stuffing "GERMANY" in the description field like a sticky note jammed into a filing cabinet. It works, but it feels wrong.

Let's fix that. Here's the full journey, step by step.

🎯 User Goal
"As a user, I want to assign a country to each task so I can capture the geographic context of my work and stay organized across regions."

📍 Journey Map
Phase 1: Navigating to the Task Form
Step	User Action	System Response	Touchpoint
1	Sam logs in at /	Cookie is set, redirect to /home	landing.html
2	Sam clicks "Add New Task" (or edits an existing one)	Redirect to /task (or /task?task_id=X)	home.html → task.html
🟢 Expected Feeling: Familiar, confident. Sam knows this flow already — no friction here.

Phase 2: Discovering the New Country Field
Step	User Action	System Response	Touchpoint
3	Sam sees the task form	The form now displays a new "Country" field between Category and the action buttons	task.html
4	Sam recognizes the field immediately	The field has a clear label "Country", a placeholder like "Select a country…", and optionally a searchable dropdown	task.html
🟡 Potential Friction Points:

❓ "Is this required?" — The field should be optional with clear visual indication (no asterisk, or a subtle "optional" label). Not every task is country-specific.
❓ "There are 195 countries — how do I find mine quickly?" — A plain <select> with 195 options is painful. Consider a searchable dropdown or at minimum alphabetically sorted options with a blank default.
❓ "What if I'm editing an old task?" — Existing tasks have no country. The field must gracefully show empty/unselected for legacy tasks without breaking the form.
Phase 3: Filling In the Country
Step	User Action	System Response	Touchpoint
5	Sam clicks the Country dropdown	A list of countries appears (ideally searchable/filterable)	task.html
6	Sam types "Ger…" or scrolls to "Germany"	The option highlights / filters down	task.html
7	Sam selects "Germany"	The field populates with "Germany"	task.html
🟡 Potential Friction Points:

❓ "Do I pick the full name or a code?" — Show full country names to the user (e.g., "Germany"), store the value as either the full name or an ISO code (DE) in the backend — but the user should never see raw codes.
❓ "What about territories, disputed regions?" — For a demo/simple app, a standard ISO 3166-1 list is sufficient. Don't over-engineer.
Phase 4: Saving the Task
Step	User Action	System Response	Touchpoint
8	Sam fills out remaining fields (name, description, dates, category)	Form is ready	task.html
9	Sam clicks "Save"	POST /task sends all fields including country	task.html → server
10	Server validates and persists	Task saved to SQLite with new country column	Backend
11	Sam is redirected to /home	Dashboard shows the task list	home.html
🟡 Potential Friction Points:

❓ "I saved but where's the country on the dashboard?" — If /home doesn't display the country, Sam has no confirmation it was captured. The task list on home.html should show the country (or at least show it on hover/detail view).
❓ "I submitted without a country — did it break?" — Since it's optional, the backend must accept NULL/empty. No 500 errors.
Phase 5: Editing a Task with Country
Step	User Action	System Response	Touchpoint
12	Sam clicks "Edit" on an existing task	Redirect to /task?task_id=X	home.html → task.html
13	The form pre-populates all fields including country	Country dropdown shows "Germany" pre-selected	task.html
14	Sam changes country to "Brazil" and saves	Task updated successfully	task.html → server → home.html
🟡 Potential Friction Points:

❓ "Old tasks created before this feature show a blank country" — This is fine, but the dropdown must handle None/empty gracefully by defaulting to the placeholder.
🏗️ Implementation Touchpoints Summary
Here's the concrete checklist this journey implies:

🎬 The Happy Ending
Sam opens the task form, sees the clean new "Country" dropdown, types "Ger", picks Germany, saves. Back on the dashboard, there it is — "Germany" right next to the task name. No more sticky-note hacks in the description field. Every task now has a home on the map. Sam smiles, takes a sip of coffee, and moves on to the next task. The system just got out of the way — exactly as it should. ☕🌍