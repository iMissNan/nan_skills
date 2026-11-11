# 页面模板索引

来源：astryx design system 0.7.13 的 `template --skeleton` 输出。
骨架保留布局结构与间距数值（`padding`、`gap`、`columns`），**属性仍是 JSX 写法**（如 `padding={6}`），需按目标框架改写语法。
上游最多输出 35 行，超出部分以 `...` 省略，须按 description 自行补全。

共 58 个页面模板，721 个区块模板。

> 更新：`python scripts/update_templates.py --write`。本文件与 `snapshot.json` 由该脚本重新生成。

## 页面模板

| id | 名称 | 适用场景 |
|---|---|---|
| `ai-chat` | AI Chat Conversation | Transcript of alternating turns carrying mixed rich content inline (markdown, code blocks, collapsible tool-call output) beside a resizable artifact panel that holds generated output while the stream keeps scrolling. |
| `ai-chat-landing` | AI Chat Landing | Zero-state entry surface centered on a single composer with suggestion chips instead of history, sized for the moment before any content exists. The empty counterpart to a transcript. |
| `dashboard` | Analytics Dashboard | Three-band analytics: a row of headline tiles, then charts, then supporting tables, all re-reading from one global filter bar. Breadth over depth, a summary surface rather than a drill-down. |
| `login` | Basic Login | Minimal centered credential form on a plain ground: two fields and a submit, nothing competing for attention. The least-chrome entry surface. |
| `blank` | Blank | Bare scaffold: one heading slot, one empty content region, no navigation and no chrome. The starting point when every other layout imposes more structure than wanted. |
| `canvas-editor` | Canvas Editor | Layered artboard workspace: document tabs over a layer rail, a fixed-size frame you zoom on a muted backdrop, and an inspector of position, type, and filter fields that retargets to the selected layer. Objects hold a coordinate rather than reflowing, so moving one never moves another. |
| `library` | Card Grid | Searchable, browsable card grid with filter tabs and a real empty state: uniform tiles organized by topic, narrowing in place, with no detail surface behind them. |
| `centered-hero` | Centered Hero | Symmetrical centered stack (headline, short blurb, paired call-to-action buttons) resting on one wide full-bleed picture, with nothing on either flank competing. |
| `payment-form` | Checkout Form | Long sectioned form running beside a summary that stays visible while the fields scroll and recalculates as they change, ending on a terminal confirm of the total. Sections run contact, address, delivery choice, then card details. |
| `checkout-wizard` | Checkout Wizard | Multi-step checkout, cart, order, and payment wizard with a running summary that recalculates as answers change. It adapts to its host width, renders the summary first on narrow surfaces, validates every forward path, and completes locally without sending payment. |
| `classic-gallery` | Classic Gallery | Uniform grid of equal-ratio media tiles under a centered intro, with filter tabs that narrow the set in place. Regular rhythm, unlike the variable-height masonry variant. |
| `table-collapsible` | Collapsible Table | Several tables on one page, each in a collapsible card with its own columns — for groups that do not share a schema, where one table would stand full of empty cells. One time range drives them all, and rows expand into a history chart. Accounts, integrations, sections, sort, expand, or collapse. |
| `table-comparison` | Comparison Table | Transposed matrix that puts candidates in the columns and criteria in grouped rows, with a pinned label column that survives horizontal scroll, columns you can swap or add, and best-in-row marks you can toggle. Compare, comparison, matrix, spec sheet, feature grid, pricing table, benchmark, frozen column, sticky column, or side-by-side. |
| `contact-form` | Contact Form | Flat single-column form mixing control types (text, pill toggles, dropdowns, long free-text) landing on one full-width submit. No steps, no branching, no summary rail. |
| `course-detail` | Course Detail | Long-form sales page for a single offering, in two columns — read the pitch, then enroll from a sticky rail. The main column holds a preview poster with a fact row, an about block with skill chips, a module syllabus whose sections collapse module by module, an instructor card, reviews with a scored-aspects panel, and a FAQ; the rail holds the price, a self-paced or cohort start picker, and a weekly-pace slider that computes a finish date. The shape for any offering with a curriculum and a purchase panel — a course, class, masterclass, bootcamp, workshop, or training. |
| `dashboard-comparison` | Data Dashboard | Comparison-heavy analytics behind a persistent filter bar: tiles that each carry an inline sparkline and several period-over-period deltas, then segmented breakdowns underneath. Every number is shown against another number. |
| `form-wizard-dialog` | Dialog Wizard | Step through a short flow in a dialog, overlay, or popup launched from the page underneath, which stays where it was. Compact step markers and a pinned action row inside a constrained width, rather than the full page a wizard usually gets. Best for two to four short steps — setup, invite, schedule, onboarding — where losing the context underneath would cost more than the flow is worth. |
| `documentation` | Documentation Catalog | Reference landing that is pure wayfinding: a banner above a grid of category cards linking into sections, with no article content on the surface itself. |
| `documentation-design` | Documentation Design | Reference article alternating prose with live rendered examples: an interactive preview, a property table, paired do and don't comparisons, and copyable code blocks. |
| `documentation-technical` | Documentation Technical | Reference article ordered as sequential numbered steps with code at each stage, plus callout cards for prerequisites and onward links. A linear walkthrough rather than a browsable reference. |
| `dashboard-scorecard` | Executive Summary Dashboard | Report-shaped analytics with a prose rail beside the charts: a scorecard of headline numbers with period deltas and status coloring, goal-attainment bars, a trend grid, and a written commentary column that folds beneath the content when narrow. |
| `file-explorer` | File Explorer | Hierarchical browser that drills through nested levels as adjacent columns rather than replacing the list each time, with breadcrumb history, switchable list and grid density, and a metadata pane for the selected node. |
| `table-filter` | Filterable Table | Flat row collection built around progressive filtering: a token bar that escalates into full query syntax, saved views that persist a filter set, column and grouping options, and a resizable detail pane. |
| `form-wizard` | Form Wizard | Linear multi-step form that moves through one panel at a time, with a horizontal progress track pinned above rather than running down a rail, so every step keeps the full content width for its fields. Only the current step renders, unlike an accordion where each section expands into one long scrolling form. Each advance is validated, and a step left broken stays flagged to jump back to. |
| `dashboard-cohort-funnel` | Funnel & Cohort Dashboard | Analytics for sequence and retention questions, pairing two shapes a plain dashboard cannot hold: a staged funnel where each step reads as drop-off against the one before, and a two-axis cohort matrix rendered as a heatmap. |
| `gallery-hero` | Gallery Hero | Centered stack (headline, short blurb, call-to-action buttons) resolving into a multi-image photo grid rather than one wide full-bleed picture, so the imagery reads as a set. |
| `table-grouped` | Grouped Table | Row collection bundled into collapsible sections with per-group counts, so a long list reads as a handful of blocks that expand and collapse. Query filtering and a resizable inspector for the selected row. |
| `ide` | IDE | Dense multi-pane workspace of resizable, collapsible regions: a hierarchy tree on one flank, tabbed documents in the middle, a docked drawer along the bottom, an inspector opposite. Drag a divider to resize or collapse any of them. |
| `table-inbox` | Inbox Table | Two-pane message queue: the table indexes a reading pane rather than being the destination, with a divider you drag to resize. Rows stack when the table narrows, not the window; threads read as collapsible messages; replying opens a composer that leaves the list live. |
| `incident-console` | Incident Console | Dense row queue with an inspector: severity-coded rows grouped by status, a saved-search filter bar, a segmented status control, and a resizable detail pane for the selected row. Rows, not cards, sized for scanning volume. |
| `form-wizard-inline` | Inline Wizard | Accordion wizard stacking every step in one column: the active step expands in place while finished ones collapse to a single line carrying their result and a way back in. Steps that run themselves expand into a nested stepper that ticks check by check and halts the column where one fails. Best when later steps depend on what earlier ones decided. |
| `kanban-board` | Kanban Board | Horizontal lanes of draggable cards where the column itself is the status, so drag and drop between lanes is the state change. Fixed columns, variable-height cards. |
| `login-card` | Login Card | Credential form inside an elevated centered card, third-party provider buttons separated from the fields by a divider, secondary sign-up and legal links beneath. |
| `login-split` | Login Split | Credential form filling one half of a two-pane split, full-bleed media holding the other. Same fields as the card variant, but the layout carries brand imagery. |
| `login-sso` | Login SSO | Progressive credential flow that branches on input: the email domain resolves an identity provider and redirects, with a password path as fallback. Two-stage rather than one form. |
| `messaging-shell` | Messaging Shell | Four-column nested navigation narrowing left to right (team workspace, channel list, message stream, thread panel) where each column scopes the next. Dense rows, zero cards. |
| `mixed-gallery` | Mixed Gallery | Masonry grid of variable-height tiles that pack against each other instead of cropping to a shared ratio, captioned per tile. Irregular rhythm, unlike the uniform gallery. |
| `detail-page` | Order Detail | Single-record detail in two columns: a summary header with status and actions, a repeating line-item list, a totals block that sums it, and a chronological activity timeline in the rail. The shape for any record holding children plus a history: a customer order with shipping, an invoice, a transaction, or a job. |
| `editor` | Page Editor | Three-pane authoring workspace: a source palette on one flank, a live canvas in the middle, and an inspector that retargets to whatever is selected. Drag and drop to reorder, edit to see it render immediately. |
| `dashboard-composition` | Portfolio Dashboard | Analytics for a value-over-time question: balance and change tiles above a stacked area chart of composition through time, closing on a ranked table of the largest contributors. |
| `product-detail` | Product Detail | Single-item detail pairing a media gallery with a selection column: variant swatches, a quantity stepper, primary and secondary commit actions, and collapsible specification sections below. |
| `product-gallery` | Product Gallery | Uniform card grid where every tile carries media, title, supporting line, and a price. Browse-to-select only, with no filtering and no detail surface. |
| `dashboard-progress` | Project Status Dashboard | Status analytics mixing progress and time-axis shapes: a completion donut, a horizontal timeline of dated bars against a today marker, a per-owner table with progress and status, an at-risk list, and a burndown. |
| `table-page` | Searchable Table | Flat table of uniform rows under a block of record-level facts, narrowed three ways at once — a full-text search box, a scope toggle, and per-column popovers — with sortable and filterable columns, per-row hover detail, and totals derived from the visible rows that flag themselves as partial while a filter is on. The shape for one homogeneous list, not nested rows or groups with their own columns. |
| `dashboard-alert-rail` | Service Monitoring Dashboard | Always-on analytics with a triage rail: status-colored tiles with sparklines, multi-series time charts over a switchable window, and an independently scrolling alert column that folds into the content when narrow. |
| `settings-dialog` | Settings Dialog | Preferences inside a modal container with searchable section navigation, so configuration happens without leaving whatever is underneath. Grouped toggles, live preview of appearance choices, rebindable shortcuts. |
| `settings` | Settings Form | Preferences as one continuously scrolling form, sections stacked in order with no navigation between them. The simplest settings shape: everything reachable by scrolling. |
| `settings-sidebar` | Settings Panels | Preferences split into nav-switched panels: a persistent section list swaps the pane beside it, and rows edit in place rather than opening a separate form. |
| `shell-nav` | Shell Nav | Application frame combining both navigation axes: a top menu bar with command-palette search over a resizable hierarchy rail, wrapping placeholder content. For when one axis is not enough. |
| `side-gallery` | Side Gallery | Asymmetric split section: a copy column of headline, supporting text, and links held against a clustered image collage opposite. Deliberately off-balance, unlike the centered hero. |
| `shell-side-nav` | Side Nav | Application frame with a single collapsible, resizable left rail carrying grouped history and search, wrapping the main content. Vertical navigation only, no top bar. |
| `table` | Simple Table | Flat row collection where columns sort, rows select into a bulk-action toolbar, and each row carries an overflow menu. Sortable but ungrouped, with no detail pane, the baseline shape. |
| `theme-showcase` | Theme Showcase | Multi-surface comparison shell: preview palettes, typography, icons and control states across a storefront, checkout, chat and inventory on one responsive canvas. A theme preview and design-system showcase, with an embeddable content view for an existing app shell. |
| `shell-top-nav` | Top Nav | Application frame with horizontal navigation only: a centered bar whose items open full-width mega-menu panels, over placeholder content that keeps the entire width. |
| `table-tree` | Tree Table | Hierarchical table where every parent row rolls up from its children — a code repository whose folders show the newest commit beneath them, beside a detail sidebar and a rendered README. Columns resize, siblings sort within their own level, arrow keys walk the rows, and search prunes the tree to matching branches. |
| `form-two-column` | Two-column Form | Form split into two columns beneath a hero header: inputs on one flank, a persistent context panel opposite that stays put while the fields scroll. Flat, single submit, no steps. |
| `form-wizard-vertical` | Vertical Wizard | Multi-step wizard with the steps in a fixed left rail that stays visible while the form scrolls, plus a side panel whose guidance follows the focused field. Suits long or unequal steps carrying uploads, previews, and dense review metadata. As width tightens the guidance drops first, then the rail rotates into a horizontal stepper above the form. |
| `work-item-detail` | Work Item Detail | Single work-item detail in two columns: a title with a status selector, a description, a subtask checklist with progress, an attachments block, and a comment and activity feed in the main column, plus a property rail with assignee, dates, labels, and linked items. The shape for any tracked item with children, properties, and a comment history — a task, ticket, issue, story, bug, card, request, or work item. |

## 区块模板（前 60 个，共 721 个，全量见 astryx CLI）

| id | 名称 |
|---|---|
| `AlertDialogDeleteConfirmation` | AlertDialog — Delete |
| `AlertDialogAsyncAction` | AlertDialog — Loading |
| `AppShellShowcase` | AppShell |
| `AppShellContentOnly` | AppShell — Content Only |
| `AppShellSideNavOnly` | AppShell — Side Nav Only |
| `AppShellTopNavOnly` | AppShell — Top Nav Only |
| `AppShellTopNavWithSideNav` | AppShell — Top Nav with Side Nav |
| `AppShellWithBanner` | AppShell — With Banner |
| `AspectRatioShowcase` | AspectRatio |
| `AspectRatioWidescreen` | AspectRatio — 16:9 Widescreen Image |
| `AspectRatioCircleImage` | AspectRatio — Circle Image |
| `AspectRatioImageGallery` | AspectRatio — Image Gallery |
| `AspectRatioWithSkeleton` | AspectRatio — Loading Skeleton |
| `AspectRatioSquareImage` | AspectRatio — Square Image |
| `AvatarShowcase` | Avatar |
| `AvatarFallbackChain` | Avatar — Fallback Chain |
| `AvatarGroup` | Avatar — Group |
| `AvatarInitialsFallback` | Avatar — Initials |
| `AvatarInteractive` | Avatar — Interactive |
| `AvatarWithImage` | Avatar — Photo |
| `AvatarWithStatus` | Avatar — Status Dot |
| `AvatarTooltip` | Avatar — Tooltip |
| `AvatarUserCard` | Avatar — User Card |
| `AvatarGroupShowcase` | AvatarGroup |
| `AvatarGroupInteractive` | AvatarGroup — Interactive |
| `AvatarGroupOverflowShowcase` | AvatarGroupOverflow |
| `AvatarGroupOverflowCustomText` | AvatarGroupOverflow — Custom Text |
| `AvatarGroupOverflowDefault` | AvatarGroupOverflow — Default Count |
| `AvatarStatusDotShowcase` | AvatarStatusDot |
| `AvatarStatusDotVariants` | AvatarStatusDot — Variants |
| `BadgeCategoryTags` | Badge — Colors |
| `BadgeCountBadges` | Badge — Counts |
| `BadgeStatusLabels` | Badge — Status |
| `BadgeShowcase` | Badge — Variants |
| `BannerWithActionButton` | Banner — Action |
| `BannerCollapsibleContent` | Banner — Collapsible |
| `BannerDismissable` | Banner — Dismiss |
| `BannerFloating` | Banner — Floating |
| `BannerSectionVariant` | Banner — Full Width |
| `BannerShowcase` | Banner — Statuses |
| `BannerStatuses` | Banner — Statuses |
| `BaseTypeaheadShowcase` | BaseTypeahead |
| `BaseTypeaheadCustomSearch` | BaseTypeahead — Custom Search Bar |
| `BaseTypeaheadMenu` | BaseTypeahead — Menu |
| `DrawerShowcase` | Basic |
| `BlockquoteShowcase` | Blockquote — Showcase |
| `BlockquoteTestimonials` | Blockquote — Testimonials |
| `BlockquoteWithCite` | Blockquote — With Attribution |
| `BottomSheetShowcase` | Bottom Sheet |
| `BottomSheetHeights` | Bottom Sheet — Height variants |
| `BottomSheetMobileKeyboard` | Bottom Sheet — Mobile keyboard |
| `BottomSheetSwitcherShowcase` | Bottom Sheet — Multi-step flow |
| `BottomSheetNoScrim` | Bottom Sheet — No scrim |
| `BottomSheetSwitcherReviewFlow` | Bottom Sheet — Review flow |
| `BottomSheetSnapPoints` | Bottom Sheet — Snap points |
| `BreadcrumbItemShowcase` | BreadcrumbItem |
| `BreadcrumbItemBasic` | BreadcrumbItem — Basic |
| `BreadcrumbsShowcase` | Breadcrumbs |
| `BreadcrumbsDeepHierarchy` | Breadcrumbs — Deep Path |
| `BreadcrumbsWithIcons` | Breadcrumbs — Icons |
