"""The agent: the tool-calling loop. This is the "brain + hands" wiring.

The MODEL only decides which tool to call. This loop is what actually RUNS the
tool -- which is exactly why the defense checks happen here, right before a tool
executes.

Flow:
  1. retrieve documents for the user's question
  2. build the message list (system prompt + context + question)
  3. ask the model; if it returns tool_calls, run them and feed results back;
     repeat until the model returns a plain text answer
"""
import ollama
from config import CHAT_MODEL, MAX_TOOL_ITERATIONS
from tools import REGISTRY, TOOL_SCHEMAS
from retrieve import retrieve
import defense

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using the provided context. "
    "You can use tools when they are needed to answer."
)
# Deliberately minimal: strong enough for the agent to behave usefully, but not
# hardened against this exact injection -- a prompt locked down that specifically
# wouldn't demonstrate anything. The authorization gate in defense.py is what
# enforces the safety/usefulness balance structurally instead.


def run_agent(user_question: str, defense_on: bool = False) -> str:
    # 1. Retrieve context for the question.
    sources = retrieve(user_question)
    context = "\n\n".join(f"[{src}]\n{txt}" for src, txt in sources)
    print(f"[agent] retrieved documents: {[s for s, _ in sources]}")

    # 2. Optional defense layer: mark retrieved content as untrusted data.
    if defense_on:
        context = defense.spotlight(context)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_question}"},
    ]

    # 3. The tool-calling loop.
    for _ in range(MAX_TOOL_ITERATIONS):
        resp = ollama.chat(model=CHAT_MODEL, messages=messages, tools=TOOL_SCHEMAS)
        msg = resp.message
        calls = msg.tool_calls

        if not calls:
            return msg.content or "(no answer)"      # final answer -> done

        # Keep the model's tool-call turn in the history.
        messages.append(msg.model_dump())

        for call in calls:
            name = call.function.name
            args = dict(call.function.arguments)

            # --- defense checkpoint: decide whether this call is allowed ---
            allowed = True
            if defense_on:
                allowed = defense.is_authorized(name, user_question)
                defense.log_tool_call(name, args, allowed)

            if not allowed:
                result = f"BLOCKED by policy: '{name}' was not authorized by the user."
            elif name in REGISTRY:
                result = REGISTRY[name](**args)       # <-- the harness ACTS here
                if not defense_on:
                    print(f"[agent] executed {name}({args}) -> {result}")
            else:
                result = f"unknown tool: {name}"

            # Feed the tool result back so the model can continue.
            messages.append({"role": "tool", "content": str(result)})

    return "(stopped: hit the max tool-iteration limit)"
