Build a fullstack boilerplate project that combines a Django backend and a Next.js frontend.

The goal is to create a robust & reusable starter kit for future projects. This is not the final product itself, but a clean foundation that will later be used to build other applications.

## Project context

I already have an existing Django boilerplate that includes the backend setup and conventions I usually like to have in my Django projects.

For this new project, I want to use that existing Django boilerplate as the base and extend it into a fullstack boilerplate with:

* a Django backend
* Django REST Framework for the API layer
* a Next.js frontend connected to the backend
* authentication handled with Allauth Headless

## Objective

Create a new boilerplate that provides a minimal but working integration between Django and Next.js.

The purpose is to establish a solid starting point with backend and frontend connected properly, so future feature development can happen on top of it.

## Django base boilerplate

I have a way of doing things and to start a Django project, to respect that habit please use this boilerplate as a base : https://github.com/Cap0n3/barebone.git

## Backend requirements

The backend should:

* be based on my existing Django boilerplate
* integrate Django REST Framework
* use Allauth Headless for authentication
* expose the necessary API endpoints for basic frontend communication
* support frontend-friendly authentication flows
* remain clean, modular, and reusable as a long-term starter project

## Frontend requirements

The frontend should:

* use Next.js
* be connected to the Django backend
* include a very simple initial interface to validate that the connection works
* integrate with the Allauth Headless authentication flow
* use Shadcn/UI for user interface (components)
* include a minimal authentication flow with:

  * sign up
  * sign in / login
  * authenticated session handling
  * logout

## Scope

This first step should stay intentionally simple.

The goal is not to build the final application yet, but to produce a functional fullstack boilerplate with:

* Django + Django REST Framework on the backend
* Allauth Headless for authentication
* Next.js on the frontend
* basic API connectivity
* basic authentication working end to end

## Expected outcome

The final result should be a clean and reusable fullstack boilerplate that I can use as the foundation for future SaaS projects.

It should demonstrate:

* a working Django backend based on my existing boilerplate
* Django REST Framework integrated properly
* Allauth Headless configured for frontend-driven authentication
* a connected Next.js frontend
* a minimal test page or interface
* basic sign up, sign in, and logout functionality
* authenticated session handling between frontend and backend
* a structure that is easy to extend later

## Technical direction

This boilerplate should treat the Django backend as an API-first backend and the Next.js app as the frontend client.

Authentication should be implemented using Allauth Headless so that the frontend fully controls the user interface and communicates with Django through API-based authentication flows rather than server-rendered Django auth pages.
The frontend should use Shadcn/UI components for the user interface, and the overall structure should be modular and clean to facilitate future development.

## UI components — MANDATORY rule

**Always use shadcn/ui components from `@/components/ui/*`. NEVER hand-write UI primitives** (alert, dialog, dropdown, toast, tabs, select, etc.).

- The project is already initialized with shadcn (`frontend/components.json` exists, style is `radix-nova`, base color `neutral`, CSS variables enabled).
- If a needed component is missing from `frontend/components/ui/`, **STOP and ask the user to run the install command** — do not fabricate a substitute. The canonical command is:
  ```bash
  cd frontend && pnpm dlx shadcn@latest add <component>
  ```
- The shadcn CLI is interactive and writes files using the project's configured style, so Claude must not bypass it by writing `*.tsx` in `components/ui/` by hand.
- Only compose/extend existing shadcn components in feature code (`app/**`, `components/<feature>/**`) — never duplicate primitives.