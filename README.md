# readme

this is a library i made to work with datastar

i probably won't maintain it

i did this in a hurry so a lot of chatgpt was used, use at your own risk


## Features

- **SSE Events**:
  - `MergeFragmentsEvent`
  - `RemoveFragmentsEvent`
  - `MergeSignalsEvent`
  - `RemoveSignalsEvent`
  - `ExecuteScriptEvent`
- **Signal Parsing**:
  - `ReadSignals` fastapi style helper for extracting signals from incoming requests.
---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/fredmonroe/datastar-python.git
   cd your-repo
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage Examples

### DataStar SSE Events

#### Example: `MergeFragmentsEvent`

```python
merge_event = MergeFragmentsEvent(
    data="<div id='example'>New Content</div>",
    selector="#example",
    merge_mode=FragmentMergeMode.INNER,
    settle_duration=500,
    use_view_transition=True,
    event_id="merge-1",
    retry_duration=2000,
)

print(str(merge_event))
```

**Output**:
```
event: datastar-merge-fragments
id: merge-1
retry: 2000
data: selector #example
data: merge inner
data: settleDuration 500
data: useViewTransition true
data: fragments <div id='example'>New Content</div>
```

#### Example: `RemoveSignalsEvent`

```python
remove_event = RemoveSignalsEvent(
    paths=['user.settings', 'app.theme', 'notifications'],
    event_id="remove-1",
    retry_duration=2000,
)

print(str(remove_event))
```

**Output**:
```
event: datastar-remove-signals
id: remove-1
retry: 2000
data: paths user.settings app.theme notifications
```

#### Example: `ExecuteScriptEvent`

```python
script_event = ExecuteScriptEvent(
    script="console.log('Hello, World!');",
    auto_remove=False,
    attributes=["async true", "defer true"],
    event_id="script-1",
    retry_duration=1500,
)

print(str(script_event))
```

**Output**:
```
event: datastar-execute-script
id: script-1
retry: 1500
data: autoRemove false
data: attributes async true
data: attributes defer true
data: script console.log('Hello, World!');
```

---

### Signal Management with Dependency Injection

#### `ReadSignals` Dependency

The `ReadSignals` function parses incoming signals from the browser and returns them as a dictionary.

**Example Usage in a Route**:

```python
@app.post("/parse-signals")
async def parse_signals(parsed_signals: Dict[str, Any] = Depends(ReadSignals)):
    return {"status": "success", "data": parsed_signals}
```

#### `MergeSignals` Dependency

This shows how you could create your own `MergeSignals` dependency merges parsed signals into a store and returns the updated store.

**Example Store and Dependency**:

```python
signal_store = {}

@app.post("/merge-signals")
async def merge_signals(merged_store: Dict[str, Any] = Depends(MergeSignals)):
    return {"status": "success", "merged_signals": merged_store}
```

**Example Request**:

```bash
curl -X POST "http://127.0.0.1:8000/merge-signals" \
     -H "Content-Type: application/json" \
     -d '{"key": "new_value", "nested": {"key2": "new_value2"}}'
```

**Response**:
```json
{
  "status": "success",
  "merged_signals": {
    "key": "new_value",
    "nested": {
      "key2": "new_value2"
    }
  }
}
```

---

### Example SSE Endpoint

This is an example `/sse` endpoint streams Server-Sent Events (SSE) to the client using the implemented event classes.

**Example Implementation**:

```python
@app.get("/sse")
async def sse_endpoint():
    async def message_generator():
        merge_event = MergeFragmentsEvent(
            data="<div id='example'>New Content</div>",
            selector="#example",
            merge_mode=FragmentMergeMode.INNER,
            settle_duration=500,
            use_view_transition=True,
            event_id="merge-1",
            retry_duration=2000,
        )
        yield str(merge_event)
        await asyncio.sleep(2)

        remove_event = RemoveSignalsEvent(
            paths=['user.settings', 'app.theme'],
            event_id="remove-1",
            retry_duration=2000,
        )
        yield str(remove_event)
        await asyncio.sleep(2)

    return StreamingResponse(message_generator(), media_type="text/event-stream")
```
