---
title: "Flutter forms past the toy example: async validation, focus, and autofill"
description: "Form and TextFormField cover the tutorial. Real forms need validation that talks to a server, errors that appear at the right moment, focus that moves like the platform expects, and a keyboard that does not cover the field being typed into."
seoDescription: "Building real Flutter forms: autovalidateMode, async and cross-field validation, FocusNode traversal, TextInputFormatter, AutofillGroup, and controller lifecycle."
keywords:
  - flutter form validation async
  - autovalidatemode flutter
  - flutter focusnode next field
  - textinputformatter flutter example
  - flutter autofillgroup password manager
  - texteditingcontroller dispose
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-04"
emoji: "📝"
tags: ["Flutter", "Forms", "Validation", "UX", "Accessibility"]
sources:
  - name: "Form — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Form-class.html"
  - name: "FormField — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/FormField-class.html"
  - name: "TextFormField — Flutter API"
    url: "https://api.flutter.dev/flutter/material/TextFormField-class.html"
  - name: "Flutter cookbook — Build a form with validation"
    url: "https://docs.flutter.dev/cookbook/forms/validation"
  - name: "TextInputFormatter — Flutter API"
    url: "https://api.flutter.dev/flutter/services/TextInputFormatter-class.html"
  - name: "AutofillGroup — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/AutofillGroup-class.html"
related:
  - slug: "flutter-accessibility-semantics"
    title: "Flutter accessibility: what the semantics tree actually reports"
  - slug: "flutter-build-context-explained"
    title: "BuildContext is an element: reading the error messages that mention it"
draft: false
---

The Flutter form cookbook gets you to a working sign-up screen in about forty lines. Then a designer looks at it and you discover that the errors flash before anyone has typed, the Enter key does nothing, the password manager ignores the fields, and on a small phone the keyboard covers the field you are editing. None of those are validation problems. They are the parts of "a form" that the tutorial does not model.

## The three objects, and what each owns

`Form` is a coordinator, not a layout. It holds a `FormState` that can `validate()`, `save()` and `reset()` every `FormField` beneath it in the tree. `FormField` owns one value, its error string, and whether it has been touched. `TextFormField` is a `FormField` wrapped around a `TextField`.

```dart
final _formKey = GlobalKey<FormState>();

Form(
  key: _formKey,
  child: Column(children: [
    TextFormField(
      decoration: const InputDecoration(labelText: 'Email'),
      validator: (value) =>
          (value == null || !value.contains('@')) ? 'Enter a valid email' : null,
      onSaved: (value) => _draft.email = value!.trim(),
    ),
  ]),
);

if (_formKey.currentState!.validate()) {
  _formKey.currentState!.save();
  await api.signUp(_draft);
}
```

A `validator` returns `null` for valid and a message for invalid — that inversion trips everyone once. `onSaved` runs only when you call `save()`, which makes "validate, then commit" a natural two-phase flow.

The `GlobalKey` must be a **field**, not a local in `build`. A key recreated each build is a new identity every frame, and `currentState` will be null or stale exactly when you need it.

## When errors appear is a UX decision, not a default

`autovalidateMode` has three values and the wrong one is the most common form complaint:

| Value | Validates | Feels like |
| --- | --- | --- |
| `disabled` (default) | Only on explicit `validate()` | Nothing until submit — safe, a bit late |
| `onUserInteraction` | After the user has edited that field | What people expect |
| `always` | On every build, from first paint | Red errors on an empty form |

`always` on a fresh sign-up screen greets the user with three errors for fields they have not seen. Use `onUserInteraction` on the `Form` for the common case, and reserve `always` for a form pre-filled with data that is genuinely invalid.

A refinement worth the ten lines: validate on submit, but once a field has failed, switch that field to validating on change so the error clears as soon as the user fixes it. `onUserInteraction` approximates this well enough that most teams stop there.

## Cross-field rules need the value, not the widget

"Confirm password must match password" cannot be expressed by a validator that only sees its own value. Keep the source of truth in a controller and close over it:

```dart
final _password = TextEditingController();

TextFormField(
  controller: _password,
  obscureText: true,
  validator: (v) => (v == null || v.length < 8) ? 'At least 8 characters' : null,
),
TextFormField(
  obscureText: true,
  validator: (v) => v != _password.text ? 'Passwords do not match' : null,
),
```

The subtlety is *when* the second field re-validates. If the user fixes the first field, the second one's error is stale until something triggers it. Either call `_formKey.currentState!.validate()` from the first field's `onChanged`, or accept that the error clears at submit. The first is more work and better.

Every `TextEditingController` and `FocusNode` you create must be disposed:

```dart
@override
void dispose() {
  _password.dispose();
  _emailFocus.dispose();
  super.dispose();
}
```

Skipping this is a genuine leak — the controller keeps listeners alive, and on a form-heavy app it shows up in DevTools memory as a growing count of retained `State` objects.

## Async validation does not fit in `validator`

`validator` is synchronous. It has to be: it runs during `validate()`, which returns a `bool` the caller acts on immediately. So "is this username taken?" cannot live there. The workable shape is to keep the async result in state and have the synchronous validator read it:

```dart
String? _usernameError;
Timer? _debounce;

void _onUsernameChanged(String value) {
  _debounce?.cancel();
  setState(() => _usernameError = null);
  _debounce = Timer(const Duration(milliseconds: 400), () async {
    final taken = await api.isUsernameTaken(value);
    if (!mounted) return;
    setState(() => _usernameError = taken ? 'That username is taken' : null);
  });
}

TextFormField(
  onChanged: _onUsernameChanged,
  validator: (v) {
    if (v == null || v.isEmpty) return 'Required';
    return _usernameError;                 // whatever the server last said
  },
)
```

Three things make this behave. The **debounce** stops a request per keystroke. The `mounted` check stops the callback writing to a disposed state after the user navigated away. And clearing `_usernameError` at the start of each change means the form does not show a stale "taken" while a newer check is in flight.

The remaining hole is the race: submit while a check is pending and `validate()` reads the previous answer. For anything that matters, the server must re-check on submit anyway — client-side async validation is a UX affordance, not a guarantee.

## Focus is a first-class part of the form

Two behaviours users notice immediately when they are missing: the Enter/Next key moving to the next field, and the keyboard type matching the content.

```dart
TextFormField(
  keyboardType: TextInputType.emailAddress,
  textInputAction: TextInputAction.next,
  onFieldSubmitted: (_) => FocusScope.of(context).nextFocus(),
),
TextFormField(
  obscureText: true,
  textInputAction: TextInputAction.done,
  onFieldSubmitted: (_) => _submit(),
),
```

`FocusScope.of(context).nextFocus()` follows the natural traversal order, so you usually do not need to hold a `FocusNode` per field at all. Reach for explicit nodes when you need to *jump* somewhere — most usefully, moving focus to the first invalid field after a failed submit, which is both a usability win and an accessibility requirement, since a screen reader user otherwise has no idea what went wrong.

`keyboardType` is not cosmetic. `TextInputType.emailAddress` puts `@` on the primary keyboard; `TextInputType.numberWithOptions(decimal: true)` gives a numeric pad. Combine with `textCapitalization` — `TextCapitalization.words` for names, `none` for emails, where the default sentence capitalisation actively fights the user.

## Formatters shape input; they do not validate it

```dart
TextFormField(
  keyboardType: TextInputType.number,
  inputFormatters: [
    FilteringTextInputFormatter.digitsOnly,
    LengthLimitingTextInputFormatter(11),
  ],
)
```

Formatters run on every keystroke and can rewrite the value. Two rules keep them from becoming a source of bugs: never use one to enforce a business rule the user cannot see (silently dropping characters reads as a broken keyboard), and be careful with custom formatters that reposition the cursor — a formatter that inserts spaces into a card number must recompute `TextEditingValue.selection`, or typing in the middle jumps the caret to the end.

`FilteringTextInputFormatter.digitsOnly` and `LengthLimitingTextInputFormatter` cover most real needs. Anything more complex is usually clearer as a validator plus a display formatter.

## Autofill, so password managers see your fields

This is a handful of lines that meaningfully improves conversion and gets skipped constantly:

```dart
AutofillGroup(
  child: Column(children: [
    TextFormField(
      autofillHints: const [AutofillHints.username, AutofillHints.email],
      keyboardType: TextInputType.emailAddress,
    ),
    TextFormField(
      autofillHints: const [AutofillHints.password],
      obscureText: true,
      onFieldSubmitted: (_) {
        TextInput.finishAutofillContext();     // offer to save the credential
        _submit();
      },
    ),
  ]),
)
```

`AutofillGroup` tells the platform these fields belong to one credential. `autofillHints` says what each one is. `TextInput.finishAutofillContext()` is the part that prompts iOS or Android to *save* a new password — without it, sign-up flows never offer to store anything. For a new-account form use `AutofillHints.newPassword` on the password field so the manager suggests a generated one instead of an existing one.

## The keyboard covering the field

On a long form inside a `Scaffold`, the default `resizeToAvoidBottomInset: true` shrinks the body when the keyboard appears — which does nothing if your content is not scrollable. Put the form in a `SingleChildScrollView`, and the framework scrolls the focused field into view automatically.

Two things still go wrong. A `Column` inside a `SingleChildScrollView` inside a `Column` produces unbounded-height errors; give the scroll view a bounded parent (`Expanded`, or make it the direct `body`). And bottom action buttons that must stay visible belong in `bottomNavigationBar` or a `SafeArea`-wrapped bottom sheet, not at the end of the scrolling column where the keyboard pushes them out of reach.

## FAQ

**Should I use a form package or plain `Form`?**

Plain `Form` is enough for most screens and has no dependency cost. A package earns its place with dynamic schema-driven forms, or when you want the field state as a stream to feed into a state-management layer.

**Why does `validate()` return true when a field is clearly wrong?**

Either the field is not a descendant of that `Form` in the element tree, or the validator returns a non-null value only in a branch that is not being hit. Print inside the validator — it is called exactly once per field per `validate()`.

**Do I need a `TextEditingController` for every field?**

No. `onSaved` plus `initialValue` covers read-at-submit. Add a controller when you need to read or set the text between builds — cross-field validation, clearing a field, or programmatic input.

**How do I show a server-side error on a specific field after submit?**

Keep a `Map<String, String>` of field errors in state, have each validator consult it, and call `validate()` after the response arrives. That reuses the same rendering path as client-side errors instead of inventing a second one.

**Does `autovalidateMode` on the `Form` override the fields?**

A field's own `autovalidateMode` wins where it is set. Setting it on the `Form` is the convenient default; override per field for the one input that needs different timing.

---

*API behaviour here is from the Flutter widget documentation and cookbook linked above. The recommendations — `onUserInteraction` as the default, treating client-side async validation as an affordance rather than a guarantee, and moving focus to the first invalid field — are my own judgement from building forms people actually complete.*
