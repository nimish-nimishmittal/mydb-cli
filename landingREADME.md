# mydb-cli

`mydb-cli` is a CLI tool designed to simplify database branching and migration management, specifically for teams collaborating on SQL-based projects, like those using Flask. With `mydb-cli`, developers can safely make and test changes to a database schema without risking conflicts or data loss on the production environment. This tool introduces Git-like branching to MySQL databases, enabling isolated development and a safe, controlled path to apply validated changes in production.

---

## 🌟 Key Features

- **Database Branching**: Developers can create isolated database branches, ensuring safe testing and validation of changes before merging into the main branch.
- **Automated Migrations**: Allows automatic migration management with three SQL scripts: `up`, `current`, and `down`, each handling different stages of schema modification.
- **Conflict-free Collaboration**: Helps multiple developers work simultaneously on different features without worrying about database conflicts or overwrites.
- **Schema Isolation**: Each branch maintains its own database schema, enabling thorough testing and rapid changes without affecting other team members or the live environment.

---

## 💡 Problem Statement

In SQL-based applications, multiple developers often encounter schema conflicts when working on the same database. Common issues include:

- **Production Migrations Risks**: Applying database changes directly to production can introduce bugs or impact performance. In e-commerce platforms, for example, schema modifications to support features like catalog updates or order processing can corrupt live data or cause downtime, leading to a poor user experience.
- **Conflict Resolution**: Simultaneous updates by different developers can lead to conflicts, broken features, and, in worst cases, database deletion or data corruption.
- **Developer Frustration**: Altering database schemas in production can also degrade processing times, slow down application performance, and frustrate developers managing live updates.

Our solution is to introduce database branches that isolate changes per developer, reducing conflict risk, and providing a way to confidently apply only validated changes in production.

---

## 🚀 How It Works

1. **Branching Mechanism**: `mydb-cli` uses database branches (`main`, `nimish`, `mammoth`, etc.) to allow isolated development. Each branch, except `main`, has its unique schema, such as `mydb_nimish` for the `nimish` branch.
2. **Versioned Migrations**: Each branch has versioned migrations (`0000`, `0001`, etc.) containing `up`, `current`, and `down` scripts to track schema changes and enable rollbacks as needed.
3. **Automated Rollback**: When unwanted changes are detected, `mydb-cli` can automatically revert to a previous state by executing reverse queries.
4. **Migration Management**: With branch-specific migration numbering, each developer’s changes are organized and isolated, ensuring seamless merging and deployment of validated features.

---

## 🛠️ Challenges Faced

### Bytearray Handling in MySQL Drivers
One major challenge was managing database and table names returned as bytearrays instead of strings, causing errors in schema queries. This issue, unique to certain MySQL drivers, led to invalid table names during SQL execution, blocking essential schema retrieval. Diagnosing and resolving this required decoding bytearrays to strings, adding complexity but ensuring compatibility and avoiding runtime errors.

---

## 📸 Screenshots

Below are sample screenshots of the landing page.

![Screenshot 1](image.png)
![Screenshot 2](image-1.png)

---

## 🤔 Why `mydb-cli`?

`mydb-cli` provides a lightweight, branch-based alternative to traditional migration workflows, focusing on isolated, Git-like branching for databases. Compared to platforms like PlanetScale, which offers a full suite of database management tools, `mydb-cli` is simpler, straightforward, and ideal for those who want control over every step of migration management without vendor lock-in.

---

## 🏗️ Future Plans

- **Enhanced Migration History**: Display a graphical history of migrations for better tracking.
- **Schema Diffing**: Introduce automated diffing to preview schema changes before they’re applied.
- **Improved Rollback Options**: Make it easier to customize and control rollbacks per branch.

---