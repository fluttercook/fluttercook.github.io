---
title: "Stop parsing prose: schemas, tool calling, and output you can type-check"
description: "The path from regexing free text out of a model, to asking for JSON in the prompt, to a schema enforced at the API layer. Each step deletes a class of bug — and the last one still can't tell you whether the answer is true."
seoDescription: "How JSON Schema and tool calling turn LLM output into typed data: schema design, validation and retry, streaming partial JSON, and why valid is not correct."
keywords:
  - llm structured output
  - json schema tool calling
  - pydantic llm output validation
  - constrained decoding json
  - streaming partial json llm
  - llm output validation retry
category: "Deep Dive"
topic: "AI Engineering"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "📐"
tags: ["AI", "LLM", "Python", "JSON Schema", "Pydantic"]
sources:
  - name: "Claude — Structured outputs"
    url: "https://platform.claude.com/docs/en/build-with-claude/structured-outputs"
  - name: "Claude — Tool use overview"
    url: "https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview"
  - name: "Claude — Streaming"
    url: "https://platform.claude.com/docs/en/build-with-claude/streaming"
  - name: "Understanding JSON Schema"
    url: "https://json-schema.org/understanding-json-schema"
  - name: "Pydantic documentation"
    url: "https://docs.pydantic.dev/latest/"
related:
  - slug: "what-the-research-says-about-prompt-engineering"
    title: "What the research actually says about prompt engineering — five claims, fact-checked"
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "The chief-of-staff pattern: turning scattered AI chats into an agent team"
draft: false
---

Every LLM feature that touches a database starts the same way. You ask the model to classify a support ticket, it answers `This looks like a billing issue, probably high priority.`, and you write a regex. It works. You ship it. Two weeks later the model says `I'd categorise this as billing-related` and your regex returns `None`, your `if severity == "high"` branch silently evaluates false, and a critical ticket sits in the low-priority queue for three days.

Nothing broke. No exception was raised. The model did not hallucinate. It just phrased a correct answer differently, and your parser — which was never a parser, only a pattern guess — quietly disagreed.

The fix people reach for first is to ask harder: "respond with JSON only, no markdown." That helps, and it moves the failure rather than removing it. The real fix is to stop treating the response as text you interpret and start treating it as a value the API is constrained to produce. That is what JSON Schema and tool calling actually buy you.

This is a walk through the three stages, what each one removes, how to design a schema a model can fill without straining, and the failure that survives all of it: a response that validates perfectly and is still wrong.

## Three stages, three different classes of bug

| Stage | What you write | Bug class it removes | Bug class still live |
| --- | --- | --- | --- |
| Regex over prose | `re.search(r"priority: (\w+)", text)` | — | Phrasing drift, formatting drift, silent `None` |
| "Return JSON" in the prompt | `json.loads(strip_fences(text))` | Phrasing drift | Fences, prose preamble, wrong keys, wrong types |
| Schema at the API layer | `output_config={"format": {...}}` or a `strict` tool | Everything syntactic | Semantics — a valid answer that isn't true |

Read that last column downward. Each step buys you a category of problem you never have to write code for again. Nothing buys you the bottom row.

## Regex over prose fails on the model's good days

The thing that makes prose parsing so hard to catch in review is that it fails on *correct* output. If the model got the answer wrong, at least you would see a wrong answer. Instead the model gets it right and expresses it in a form your regex was not written for, and the failure looks exactly like "no match."

That gives you two bad options at the call site: raise on no-match (now correct answers crash your pipeline), or fall back to a default (now correct answers become the default, invisibly). Most codebases pick the second, because the first one pages someone. That is how you end up with a classifier whose real output distribution is 60% `"unknown"` and nobody notices for a quarter.

The deeper problem is that natural language has no boundary between the answer and the commentary about it. `Probably high, though it depends on the SLA tier` contains your value and a hedge, and no regex can tell you where the hedge starts.

## Asking for JSON moves the failure, it doesn't delete it

Put "reply with a JSON object and nothing else" in the prompt and the shape of the failure changes. You now get, in rough order of frequency:

- The JSON wrapped in a ` ```json ` fence.
- A polite sentence before the object.
- Correct JSON with a key you didn't ask for, or a key you asked for spelled differently (`customerId` vs `customer_id`).
- `"severity": "High"` when your enum is lowercase.
- `"severity": "high-ish"`, because the model had genuine uncertainty and free-text strings gave it a place to put it.
- Truncation, because the object ran past `max_tokens` and now the last brace is missing.

So you write the defensive parser. Strip fences. Find the first `{` and the last `}`. Lowercase the enum values. Coerce `"3"` to `3`. Handle the missing brace. This code grows every time you see a new failure in the logs, it is never done, and — this is the part that matters — **it is a parser for a language nobody defined.** You are reverse-engineering a format from samples of it.

The prompt is a request. It is not an invariant.

## A schema at the API layer is an invariant

Both major structured-output mechanisms move enforcement out of your prompt and into the request itself. The schema is applied while the response is being generated, so a token that would break the schema is not a token the model can emit. You are not asking any more.

Raw JSON Schema, as an output format on the response:

```python
import json, anthropic

client = anthropic.Anthropic()

TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "evidence": {
            "type": "string",
            "description": "Verbatim quote from the ticket that decided the category.",
        },
        "category": {
            "type": "string",
            "enum": ["billing", "bug", "feature_request", "account", "other"],
        },
        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "customer_id": {
            "type": ["string", "null"],
            "description": "Customer ID if the ticket states one. null if it does not.",
        },
        "needs_human": {"type": "boolean"},
    },
    "required": ["evidence", "category", "severity", "customer_id", "needs_human"],
    "additionalProperties": False,
}

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": ticket_text}],
    output_config={"format": {"type": "json_schema", "schema": TRIAGE_SCHEMA}},
)

data = json.loads(next(b.text for b in response.content if b.type == "text"))
```

Two details in that schema are load-bearing and easy to skip. `additionalProperties: False` is what stops invented keys. And `customer_id` is in `required` *and* nullable — under a strict schema, "optional" is normally expressed as a required field that is allowed to be `null`, not as a key that may be absent. That is better for you anyway: an explicit `null` means the model considered the field and had nothing; an absent key is ambiguous between "nothing to report" and "forgot."

The Pydantic path is the same guarantee with a type your editor understands:

```python
from typing import Literal
from pydantic import BaseModel, Field

class TicketTriage(BaseModel):
    evidence: str = Field(
        description="Verbatim quote from the ticket that decided the category."
    )
    category: Literal["billing", "bug", "feature_request", "account", "other"]
    severity: Literal["low", "medium", "high", "critical"]
    customer_id: str | None = Field(
        default=None, description="Customer ID if stated in the ticket, else null."
    )
    needs_human: bool
    unresolved: list[str] = Field(
        default_factory=list,
        description="Questions you could not answer from the ticket alone.",
    )

response = client.messages.parse(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": ticket_text}],
    output_format=TicketTriage,
)

triage: TicketTriage = response.parsed_output
```

`str | None` needs Python 3.10+. `parsed_output` is a real `TicketTriage`, so `triage.severity` is a `Literal` your type checker can exhaustively match on, and a typo in a branch is a build error rather than a 2 a.m. discovery.

## Output format or tool call? They answer different questions

The two mechanisms look interchangeable in a tutorial and are not.

| | Output format (`output_config.format`) | Tool call (`strict: true` on a tool) |
| --- | --- | --- |
| Shape of every response | One schema, always | The model picks which tool, or none |
| Natural meaning | "Return this record" | "Do this thing, with these arguments" |
| Multiple shapes | No | Yes — one per tool |
| Model can decline | No | Yes, by not calling anything |
| Fits | Extraction, classification, grading | Agents, routing, side effects |

If every request must produce exactly one record of one shape, use the output format — a forced single tool is just a clumsier version of the same thing. If the model is choosing among actions, or may legitimately do nothing, use tools; the choice *is* the information you want.

```python
TRIAGE_TOOL = {
    "name": "record_triage",
    "description": "Record the triage decision for one support ticket.",
    "strict": True,
    "input_schema": TRIAGE_SCHEMA,
}

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    tools=[TRIAGE_TOOL, ESCALATE_TOOL],
    messages=[{"role": "user", "content": ticket_text}],
)
```

One rule with tool inputs: always `json.loads` / read them as parsed values, never string-match on the serialised input. Escaping of Unicode and slashes varies between models, and a substring check that works today is a silent breakage waiting for the next model version.

## Designing a schema the model can actually fill

A schema is not only a contract. It is also, in a very literal sense, part of the prompt — field names and `description` strings are read by the model. Which means schema design is prompt design, and the same things help.

**Flat beats deeply nested.** Every level of nesting is more open structure the model must keep balanced while also doing the actual task, and it makes your validation errors less useful ("failed at `items[3].meta.tags[1]`" tells you much less than "failed at `severity`"). If you have a natural hierarchy, consider whether a flat record with a `parent_id` gets you the same thing.

**Enums beat free strings.** A free `"severity": string` invites `"high-ish"`, `"High"`, `"P1"` — three tokens' worth of variation you then normalise by hand. An enum turns the decision into a choice among fixed options, which is exactly the shape the decision actually has. Use enums anywhere the downstream code has a `switch`.

**Order the fields so reasoning comes before the verdict.** JSON objects are generated left to right. If `severity` is the first key, the model commits to a severity and then writes justification for it. Put `evidence` first and the quote is on the table before the label is chosen. This costs you nothing but field order.

**Give uncertainty somewhere to live.** This is the one people skip, and it is the highest-value field in the whole schema. A model asked for `customer_id: string` on a ticket with no customer ID will produce a plausible-looking customer ID, because the schema demands a string and there is no legal way to say "not present." Nullable fields, an `unresolved: list[str]`, a `needs_human: bool` — each one is a legal escape hatch. Without them, "I don't know" has to be expressed as a fabrication.

**Descriptions are instructions.** `"description": "ISO 8601 date, or null if the ticket gives no date"` does more work than three sentences in the system prompt, because it sits directly next to the field it governs.

## Validation and retry: what you feed back matters

Schema enforcement gives you syntactic validity. It cannot express things like "`needs_human` must be true when `severity` is `critical`", or "`customer_id` must exist in our database", or "`evidence` must be a real substring of the input." Those are your validators, and Pydantic gives you a place to put them:

```python
from pydantic import ValidationError, model_validator

class TicketTriage(BaseModel):
    # ... fields as above ...

    @model_validator(mode="after")
    def critical_needs_human(self):
        if self.severity == "critical" and not self.needs_human:
            raise ValueError("severity 'critical' requires needs_human=true")
        return self
```

When one of those fails, the retry has to carry new information. Re-sending the identical request is a coin flip, and if the schema was the problem it is a coin flip you keep losing. Append the failure as a turn the model can read:

```python
def triage_with_retry(ticket_text: str, max_attempts: int = 3) -> TicketTriage:
    messages = [{"role": "user", "content": ticket_text}]
    for attempt in range(max_attempts):
        response = client.messages.parse(
            model="claude-opus-5",
            max_tokens=1024,
            messages=messages,
            output_format=TicketTriage,
        )
        try:
            return response.parsed_output
        except ValidationError as err:
            if attempt == max_attempts - 1:
                raise
            messages += [
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": f"That failed validation:\n{err}\nFix it."},
            ]
```

Three habits regardless of framework. Cap the attempts — an uncapped retry loop against a metered API is a billing incident. Log the raw invalid output, not just the exception; the pattern in the failures usually tells you which field is badly designed. And keep retries idempotent: if attempt one already wrote a row, attempt two must not write a second.

The best outcome of a retry loop is that it teaches you to change the schema. A field that regularly fails validation is a field the model is being asked to guess.

## Streaming partial structured output

Structured output and streaming both work, but streaming JSON is not streaming prose. Tool inputs arrive as `input_json_delta` events carrying `partial_json` fragments — you accumulate them, and at no intermediate point is the buffer valid JSON:

```python
buffer = ""
with client.messages.stream(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[TRIAGE_TOOL],
    tool_choice={"type": "tool", "name": "record_triage"},
    messages=[{"role": "user", "content": ticket_text}],
) as stream:
    for event in stream:
        if event.type == "content_block_delta" and event.delta.type == "input_json_delta":
            buffer += event.delta.partial_json
            render_preview(buffer)   # buffer is NOT parseable yet
    final = stream.get_final_message()
```

To show something useful mid-stream you need a tolerant parser — one that closes any open strings, arrays and objects before parsing — and you must treat the result as a preview, never as data. On this API, setting `eager_input_streaming: true` on the tool definition makes those fragments start arriving sooner.

Two practical notes. Field order decides what a user sees first, which is another reason to put the human-readable field near the front: a `summary` that streams in immediately feels fast even when the numeric fields take another second. And nothing partial should ever reach your business logic. Render it, don't act on it. The one field you were most excited to show early is also the one most likely to change before `content_block_stop`.

## The failure that survives all of this

Here is the response your schema is perfectly happy with:

```json
{
  "evidence": "the charge on my card looks wrong",
  "category": "billing",
  "severity": "low",
  "customer_id": "CUS-4471",
  "needs_human": false
}
```

Every type checks. The enum values are legal. `additionalProperties` held. And the ticket said the customer had been double-charged for eleven months, `CUS-4471` is a customer ID the model constructed because the format was obvious from your other examples, and `severity: "low"` is simply wrong.

**Validation checks the shape of the answer. Verification checks the answer.** A schema cannot do the second one, and the more polished your structured-output pipeline gets, the easier it is to forget that — typed data *feels* trustworthy in a way a paragraph of prose never did. That feeling is the actual risk. Prose looked like something to be sceptical of. A Pydantic model looks like a row from your own database.

What actually helps:

- **Ground the identifiers.** Any ID, SKU, URL, or account number the model returns should be looked up against a real source before it is used. A well-formed ID is trivially easy to produce and the schema will bless every one of them.
- **Require an evidence span, then check it.** `assert triage.evidence in ticket_text` is one line and it catches an entire family of confabulation. If the quote isn't in the source, nothing built on it is safe.
- **Encode invariants you know.** Cross-field rules, plausible ranges, dates that must be in the past. These are the semantic checks the schema layer cannot see.
- **Sample and read.** Pull fifty outputs a week and read them against their inputs. Schema-valid-but-wrong is invisible to every automated check you have precisely because it passes them.
- **Keep the confidence fields honest.** If `needs_human` is never true, it is not working, and the escape hatch you designed is decorative.

The progression in this article is real and worth taking to the end. Regex to prompted JSON to enforced schema deletes three genuine classes of bug, and the resulting code is smaller and more boring. Just don't let the last step convince you that the remaining problem got smaller too. It didn't move at all.

## FAQ

**Do I still need to describe the format in the prompt if I have a schema?**
Repeating the field list is redundant — the schema is already in the request. What is still worth saying in the prompt is the *judgement*: what counts as `critical`, when to prefer `null` over a guess, what the evidence quote is for. Put the rules next to the fields as `description` strings and keep the prompt for context the schema can't hold.

**Why is my model returning `null` for everything?**
Usually because you added nullable fields without also giving instructions for when to use them, and null is the safest legal answer for every field. Tighten the descriptions ("null only if the ticket contains no date at all") and check whether the input genuinely contains the information — a high null rate is sometimes the schema correctly reporting that your source documents don't have the data.

**Is deeply nested output ever the right call?**
When the nesting is real — a list of line items each with the same fields is genuinely nested and flattening it would be worse. What to avoid is nesting invented for tidiness, like grouping unrelated fields under a `meta` object. If a level exists only for organisation, delete it.

**Should validation failures retry or fail loudly?**
Both, at different rates. Retry once or twice with the error fed back, because transient failures are real. But alert on the retry rate rather than only on the final exception — a pipeline that silently succeeds on attempt two every time is telling you the schema needs work, and a plain success metric hides that completely.

**Does structured output hurt answer quality?**
It can, if the schema fights the task — forcing a single label where the honest answer is "two of these apply" degrades the output regardless of how well the JSON validates. That is a schema design problem rather than an argument against schemas. Give the model the fields it needs to be accurate, including the ones for uncertainty, and the constraint costs you very little.

---

*The API shapes shown here — `output_config.format`, `strict` tools, `input_json_delta` — are Claude's, and the same three-stage progression applies across providers with different parameter names; check your provider's current docs before copying, since this surface has changed more than once. The schema design guidance and the validation-versus-verification argument are my own working opinion, formed from building these pipelines, not measured results.*
