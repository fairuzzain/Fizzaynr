<!-- AUTO-GENERATED from vet-the-number.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->
<!-- The seven questions derive from pstack's benchmark-checklist skill (Lauren Tan, MIT), rewritten for gstack. See NOTICE.md. -->
## Vet the number

A performance number is a claim, and these seven questions test the claim
before anyone acts on it. Answer each from a run, never from a reading of the
code. A one-run ballpark the user asked for is allowed: say it is one run,
still answer questions 4 and 7, and skip the rest unless the run looks wrong.
A choice between two options is never a ballpark.

Before running anything, write the sentence you expect to ship ("LCP 1.6 s →
1.1 s at the median on the dashboard page") and read what the measurement
script times, counts and ignores. Check `uptime` and `nproc`; on a busy
machine, interleave the two sides so both see the same noise, and say so.

1. **Why not double?** Name the limiter: the one resource or stage the time
   is spent in (one core at 100%, a 3 MB script parse, a serialized request
   chain, link bandwidth). Profile in a run you do not report, because
   profilers slow the work. When a change did not move the number, the
   limiter is the reason; find it before calling the change useless.
2. **Was it tuned?** Both sides run the way production runs: production
   build and flags, the same data, caches as warm or cold as users see them,
   the same versions. A side on defaults (a debug build, a cold cache, a
   missing index) makes this a comparison of configurations, not of
   implementations. Tune it and measure again, or pick no winner.
3. **Did it break a limit?** Do the arithmetic. Bytes per second against the
   link, operations per second times cost against the cores, time saved
   against the time the removed piece took. Removing a piece that took 10%
   of the run makes the run at most about 11% faster; a result past a limit
   measured something other than the work (a cache, a no-op, a bug).
4. **Did it error?** Count failures, timeouts, retries and non-success
   responses, and check that the output is right, not only present.
   Rejections are fast and retries are slow. If the script does not count
   errors, add the count before trusting the time.
5. **Does it reproduce?** At least 5 runs per side, alternating A, B, A, B,
   so warmup, lazy initialization, caches and drift favor neither side.
   Report the median and the range. A gap smaller than the run-to-run variation
   is no difference; when the call is close, use the harness's own statistics
   or a rank-sum test.
6. **Does it matter?** Put the micro number next to the end-to-end path a
   user waits on, with realistic data and concurrency, and report it as a
   share of the whole. A step that is 1% of the page can make the page at
   most 1% faster.
7. **Did it even happen?** Confirm the work ran inside the timed region:
   the request reached the server, the bytes were fetched, the frame was
   painted, the result was used. Lazy code (a promise nobody awaits, a
   generator nobody drains) and timeouts produce numbers for work that never
   ran.

### Report

Lead with the verdict: faster, slower, no measurable difference, or
inconclusive. Give the number with its unit, the run count, the range and the
limiter ("LCP 1.6 s → 1.1 s, median of 7 alternating runs per side, range 1.0
to 1.2 s after, bound by the hero image decode"). Call the verdict
inconclusive when you claim a difference but cannot name the limiter, when a
side ran untuned, or when questions 4 and 7 went unanswered, and say which. A
PR body carries one primary number; the runs, the range and the limiter
evidence go in the report file this skill writes in Phase 9.
