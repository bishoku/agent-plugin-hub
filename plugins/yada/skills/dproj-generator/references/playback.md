# Playback semantics

YADA's scheduler is an illustration engine, not a workflow interpreter. The source
contract is `src/store/scheduler.ts` at the revision in capabilities.json.

- `delay` is local to a step's computed start. Never accumulate previous durations
  globally. Timeline keys and sequenceId equal the corresponding sequence ID.
- A synchronous root step can start when a prior step targeting its source finishes;
  otherwise it falls back to the prior group's synchronous completion barrier.
  Thus different stepNumbers do not imply a universal sequential cursor.
- Async steps do not advance that barrier or establish synchronous source readiness.
  A later consumer can start before a publish finishes. For an event delivery story,
  inspect the actual schedule and use a deliberate local delay where necessary;
  don't change the real interaction to synchronous just to force ordering.
- Round-trip calls can nest: later steps originating at the target become children.
  Parent outbound transit takes half `duration`, then internal processing, then
  synchronous children, then return transit. Async children do not delay the return.
  Repeated visits to the same service can have surprising nesting; inspect playback.
- Same-number nested children use a common base time plus their individual delays.
  Root starts also depend on source readiness; equal stepNumber alone does not
  guarantee simultaneous visual starts.
- Keep `isRoundTrip` and timeline `animationMode:"roundTrip"` consistent. `repeat`
  with a positive `repeatParticleCount` illustrates traffic; it is not executable
  retry logic. For retries/compensation use explicit, labeled sequence steps.
- `internalProcess` describes target processing. Scheduler duration semantics differ
  for one-way and round-trip steps; don't assume a tooltip extends every transit.

Choose timings for comprehension: around 1000–2000 ms transit and 1500–3000 ms
processing captions is a starting point. Scale captions to text length; avoid a
multi-minute animation just because every edge has a long tooltip. Explain timings
as presentation timing unless they come from actual supplied measurements.

Before delivery inspect: initial request, nested call/return, parallel branch,
async publish→consume, failure/compensation and final state where applicable.
Check timed notes against actual playback, not sums of raw durations. For separate
success/failure scenarios, separate projects are clearer than implying both occur
in one execution. Sequence fragments label alternatives; they do not execute them.
