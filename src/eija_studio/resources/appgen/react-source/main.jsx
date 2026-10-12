import React, {useEffect, useSyncExternalStore} from "react";
import {createRoot} from "react-dom/client";
import {HeadlessMantineProvider, Button, TextInput, NativeSelect, Checkbox} from "@mantine/core";
import {useMediaQuery} from "@mantine/hooks";

// Mantine owns the native controls and accessibility structure. External CSS owns
// presentation: no injected style tag, inline style string, CDN or policy copy.
const inputClasses = {root: "ui-field", label: "ui-label", input: "ui-input", section: "ui-select-decoration", error: "ui-error"};
const components = {
  Button: {defaultProps: {unstyled: true, classNames: {root: "ui-button", inner: "ui-button-inner", label: "ui-button-label"}}},
  TextInput: {defaultProps: {unstyled: true, classNames: inputClasses}},
  NativeSelect: {defaultProps: {unstyled: true, classNames: inputClasses}},
  Checkbox: {defaultProps: {unstyled: true, classNames: {root: "ui-checkbox", body: "ui-checkbox-body", inner: "ui-checkbox-inner", icon: "ui-check-icon", label: "ui-label"}}},
};

function Notice({id, alert = false, children}) {
  const notice = state.notices[id];
  return <p id={id} className={`notice ${notice?.kind || ""}`} hidden={!notice}
    role={alert ? "alert" : "status"} aria-live={alert ? "assertive" : "polite"} tabIndex={-1}>
    {notice?.text}{children}
  </p>;
}
function Header() {
  const app = state.app, actor = app?.actors[state.actor], kind = actor && app.kinds?.[actor.role];
  const stand = {agent: "AI agent", timer: "timer", system: "external system"}[kind];
  const notes = [actor && !actor.active ? "inactive: every step is refused" : "",
    stand ? `${stand}: you stand in for its API calls` : ""].filter(Boolean);
  useEffect(() => {
    const bar = document.querySelector(".bar");
    const measure = () => document.documentElement.style.setProperty("--app-bar-height", `${Math.ceil(bar.getBoundingClientRect().height)}px`);
    const observer = new ResizeObserver(measure); observer.observe(bar); measure();
    window.addEventListener("resize", measure);
    return () => {observer.disconnect(); window.removeEventListener("resize", measure);};
  }, []);
  return <header className="bar">
    <div><h1 id="app-name">{app?.name || "Loading"}</h1>
      <details className="app-about"><summary>About this app</summary>
        <p id="app-description" className="sub">{app?.description || "Your model, running locally."}</p>
      </details></div>
    <div className="actor-box"><div className="actor">
      <label htmlFor="actor">Act as <span className="fixture-label">local fixture</span></label>
      <NativeSelect id="actor" aria-label="Act as local fixture" value={state.actor} disabled={state.writing || !app}
        onChange={event => actAs(event.currentTarget.value)}
        data={Object.entries(app?.actors || {}).map(([value, a]) => ({value, label: `${a.role} · ${value}${a.active ? "" : " · inactive"}`}))}/>
    </div><span id="actor-role" className={`role${actor && !actor.active ? " warn" : ""}`} aria-live="polite">
      {actor && [actor.role, ...notes].join(" · ")}</span></div>
    <Navigation/>
  </header>;
}
function Navigation() {
  const model = appNavigation();
  if (!model) return <p className="navigation-status muted" role="status">{state.app ? "Checked navigation is unavailable for this build." : "Loading navigation…"}</p>;
  const roots = model.destinations.filter(destination => destination.parent === null);
  function item(destination) {
    const children = model.destinations.filter(child => child.parent === destination.id && child.kind !== "action");
    return <li key={destination.id}>
      <Button type="button" className="navigation-link" data-nav-id={destination.id}
        aria-current={state.navigationSelected === destination.id ? "page" : undefined}
        disabled={state.writing || destination.record_required && !state.detail}
        title={destination.record_required && !state.detail ? "Select a record first" : destination.title}
        onClick={() => navigate(destination)}>{destination.title}</Button>
      {children.length > 0 && <ul>{children.map(item)}</ul>}
    </li>;
  }
  return <nav className="app-navigation" aria-label="Application navigation"><ul>{roots.map(item)}</ul></nav>;
}
function Field({field}) {
  const id = `field-${field.name}`, value = state.form.fields[field.name];
  const common = {id, label: field.label, className: "field-control", disabled: state.writing};
  if (field.type === "boolean") return <Checkbox {...common} checked={Boolean(value)}
    onChange={event => updateRecordField(field.name, event.currentTarget.checked)}/>;
  const props = {...common, value: value ?? "", required: field.required,
    onChange: event => updateRecordField(field.name, event.currentTarget.value)};
  if (field.type === "choice") return <NativeSelect {...props} data={[{value: "", label: ""}, ...field.choices]}/>;
  return <TextInput {...props} type={{number: "number", date: "date"}[field.type] || "text"}
    maxLength={field.type === "text" ? field.max_length : undefined} step={field.type === "number" ? "any" : undefined}/>;
}
function Records() {
  const screen = state.app?.screens.create;
  return <section className="panel" aria-labelledby="records-title"><h2 id="records-title" tabIndex={-1}>Records</h2>
    <form id="create" className="create" aria-labelledby="create-title" aria-busy={state.writing} onSubmit={submitCreate}>
      <h3 id="create-title">{screen?.title || "New record"}</h3>
      <TextInput id="title" label="Record name" placeholder="Name this record" maxLength={200} required
        value={state.form.title} onChange={event => updateRecordTitle(event.currentTarget.value)} disabled={state.writing}
        error={state.titleInvalid || undefined}
        attributes={{input: {"aria-describedby": state.titleInvalid ? "create-feedback" : undefined}}}/>
      <div id="fields" className="fields">{screenFields(screen).map(field => <Field key={field.name} field={field}/>)}</div>
      <Button type="submit" id="create-button" disabled={state.writing || !state.fresh}>
        {state.writing ? "Saving…" : screen?.button || "Create"}</Button>
      <Notice id="create-feedback" alert/>
    </form>
    <ul id="records" className="records">{state.records.map(record => <li key={record.id}>
      <Button type="button" aria-current={String(record.id === state.selected)} disabled={state.writing} onClick={() => select(record.id)}>
        <span>{record.title}</span><span className="chip">{record.state}</span>
      </Button></li>)}</ul>
    <p id="empty" className="muted" hidden={state.records.length > 0}>No records yet. Create one to start.</p>
  </section>;
}
function Values({record, screen}) {
  return <dl className="values">{screenFields(screen).map(field => <React.Fragment key={field.name}>
    <dt>{field.label}</dt><dd>{field.name in record.fields ? String(record.fields[field.name]) : "—"}</dd>
  </React.Fragment>)}</dl>;
}
function ActionChoice({option, record}) {
  const screen = state.app.screens.actions[option.action];
  const destination = destinationFor("action", option.action);
  return <div className="option">
    <Button type="button" title={option.action} className="quiet action-choice" data-allowed={String(option.allowed)}
      data-nav-id={destination?.id} aria-current={state.navigationSelected === destination?.id ? "page" : undefined}
      disabled={!destination || !option.allowed || state.writing || !state.fresh} onClick={event => openAction(option, record, event.currentTarget)}>
      {destination?.title || screen?.title || option.action}
    </Button><span className="action-destination">Next: {option.to}</span>
    {!destination ? <span className="why">This action has no checked navigation destination.</span>
      : option.role !== actorRole() ? <span className="why">for a {option.role}</span>
      : !option.allowed ? <span className="why">{option.reason}</span> : null}
  </div>;
}
function ActionScreen() {
  const opened = state.action, option = opened?.option, record = opened?.record;
  const screen = option && (state.app.screens.actions[option.action] || {title: option.action, fields: [], button: option.action});
  return <section id="action-screen" className="action-screen" aria-live="polite" hidden={!opened}>
    {opened && <><h3>{screen.title}</h3><p className="action-consequence">{record.state} → {option.to}</p>
      <Values record={record} screen={screen}/><div className="option">
        <Button type="button" disabled={state.writing || !state.fresh} onClick={() => {state.action = null; notify(); act(option.action, record);}}>
          {screen.button || option.action}</Button>
        <Button type="button" className="quiet" onClick={closeAction}>Close</Button>
      </div></>}
  </section>;
}
function Detail() {
  const detail = state.detail, record = detail?.record, role = state.app && actorRole();
  const mine = (detail?.options || []).filter(o => o.role === role), others = (detail?.options || []).filter(o => o.role !== role);
  const labels = Object.fromEntries(screenFields(state.app?.screens.create).map(field => [field.name, field.label]));
  return <section className="panel detail" aria-labelledby="detail-title" aria-busy={state.writing}>
    <h2 id="detail-title" tabIndex={-1}>{record?.title || "Select a record"}</h2>
    <p id="record-state" className="record-state" hidden={!record}>Current state <strong id="current-state" className="chip">{record?.state}</strong></p>
    <dl id="detail-fields" className="values">{Object.entries(record?.fields || {}).map(([name, value]) =>
      <React.Fragment key={name}><dt>{labels[name] || name}</dt><dd>{String(value)}</dd></React.Fragment>)}</dl>
    <ol id="flow" className="flow" aria-label="States">{(state.app?.states || []).map(value =>
      <li key={value} aria-current={value === record?.state ? "step" : undefined}>{value}</li>)}</ol>
    <div id="stranded" className="notice warn" hidden={!record || record.current_model}>
      This record was created under an earlier model or data model. Actions on it are refused (STALE_INSTANCE or STALE_DATA).</div>
    <h3>Choose an action</h3><div id="options" className="options">
      {mine.map(option => <ActionChoice key={option.action} option={option} record={record}/>)}
      {record && !mine.length && <p className="muted">{detail.options.length ? `Nothing for a ${role} to do in ${record.state}.` : "No further actions from this state."}</p>}
      {others.length > 0 && <details className="others"><summary>For other roles ({others.length})</summary>
        {others.map(option => <ActionChoice key={option.action} option={option} record={record}/>)}</details>}
    </div><ActionScreen/><Notice id="result"/>
    <h3>History</h3><ol id="history" className="history">{detail?.history.length ? detail.history.map((entry, i) =>
      <li key={entry.operation || i}>{entry.effect} by {entry.actor}, now {entry.state}</li>) : record && <li>Created</li>}</ol>
  </section>;
}
function RuntimeDetails() {
  const app = state.app, columns = [["Action", "rule-action"], ["From", "rule-from"], ["To", "rule-to"], ["Who", "rule-role"]];
  return <aside className="panel runtime-panel" aria-label="Model and runtime details">
    <details id="runtime-details"><summary><strong>Model &amp; runtime details</strong>
      <span>Inspect rules, recorded effects and build identity</span></summary>
      <div className="runtime-body"><h2 id="rules-title">Rules from the model</h2>
        <table className="rules" role="table"><caption>Allowed state changes and their required role</caption>
          <thead role="rowgroup"><tr role="row">{columns.map(([label, id]) => <th key={id} id={id} scope="col" role="columnheader">{label}</th>)}</tr></thead>
          <tbody id="rules" role="rowgroup">{Object.entries(app?.transitions || {}).map(([action, t]) =>
            <tr key={action} data-role={t.role} role="row" className={t.role === actorRole() ? "mine" : undefined}>
              {[action, t.from, t.to, t.role].map((value, i) => <td key={columns[i][1]} headers={columns[i][1]} role="cell">
                <span className="rule-label" aria-hidden="true">{columns[i][0]}</span><span className="rule-value">{value}</span></td>)}</tr>)}</tbody>
        </table><h3>Outbox</h3><ul id="outbox" className="outbox">{state.outbox.length ? state.outbox.map((item, i) =>
          <li key={item.id || i}>{item.effect} to {item.recipient}</li>) : <li>Empty</li>}</ul>
        <p className="muted small">Notifications are recorded here, not sent.</p>
        <p className="muted small">Built by EIJA Studio from model <code id="model-hash" title={app?.model_hash}>{app?.model_hash.slice(0, 12)}</code></p>
      </div></details>
    <p className="runtime-scope">Local fixture actors · real local records. No login or external delivery.</p>
  </aside>;
}
function App() {
  useSyncExternalStore(subscribe, snapshot, snapshot);
  const dark = useMediaQuery("(prefers-color-scheme: dark)");
  useEffect(() => {document.documentElement.dataset.colorScheme = dark ? "dark" : "light";}, [dark]);
  useEffect(() => {start().catch(showLoadError);}, []);
  return <HeadlessMantineProvider theme={{components}}>
    <Header/><section id="load-feedback" className="notice bad load-feedback" role="alert" hidden={!state.notices["load-feedback"]}>
      <p id="load-error">{state.notices["load-feedback"]?.text}</p>
      <Button id="retry-load" className="quiet" type="button" disabled={state.retrying || state.writing} onClick={retryLoad}>Reload app data</Button>
    </section><main className="layout"><Records/><Detail/><RuntimeDetails/></main>
  </HeadlessMantineProvider>;
}
document.documentElement.dataset.frontend = "react";
createRoot(document.getElementById("root")).render(<App/>);
