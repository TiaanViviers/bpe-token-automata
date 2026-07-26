# **CS345/CS711 Project Specification: BPE DFA Tokenization**

Computer Science, Stellenbosch University

| Modules                 | Computer Science 345 / Computer Science 711 |
|-------------------------|---------------------------------------------|
| Project format          | Semester project completed in groups of two |
| Implementation language | Python or Java, unless otherwise approved   |
| Submission deadline     | 14:00 on Monday 5 October                   |
| Submission platform     | Computer Science GitLab server              |
| Last updated            | 18 July 2026                                |

This specification defines the compulsory implementation, testing, experimental, reporting, and presentation requirements for the project. All submitted claims must be supported by executable artifacts, reproducible tests, measurements, or formal arguments.

**Core outcome.** Each group shall construct and validate a baseline BPE tokenization DFA, derive or implement a corresponding tokenizer transducer, construct a compact delayed-input token automaton, complete one or more self-chosen advanced extensions, and evaluate correctness and performance using a disciplined test and benchmarking framework.

# **1 Getting started**

Before reading the papers or writing any code, every group member shall watch the following video and work through the following post, which provides the practical background on BPE tokenization assumed throughout this specification:

<https://www.youtube.com/watch?v=zduSFxRajkE&t=337s>

<https://www.fast.ai/posts/2025-10-16-karpathy-tokenizers.html>

After this, read the two core papers on which the compulsory tasks are based: the formalization of BPE tokenization [\[6\]](#page-13-0) and the token-DFA construction [\[5\]](#page-13-1), followed by the compact-construction paper [\[4\]](#page-13-2).

# **2 Project purpose and background**

Byte pair encoding (BPE) is a widely used subword tokenization method. A BPE tokenizer begins with a base tokenization and repeatedly merges adjacent tokens according to an ordered dictionary of merge rules. The ordering is semantically significant: it determines which applicable pair is merged first and therefore determines the canonical tokenization of each input string [\[6,](#page-13-0) [17\]](#page-14-0).

This project studies BPE through formal-language and automata-theoretic methods. For a proper BPE dictionary, the set of canonical tokenizations forms a regular language. Berglund, Martens, and van der Merwe give a constructive procedure that transforms a string DFA into a context-invariant token DFA accepting exactly the canonical BPE tokenizations of the original language [\[5\]](#page-13-1). They further show that the relation between strings and canonical tokenizations can be represented by a subsequential string-to-tokenization transducer [\[5,](#page-13-1) [3\]](#page-13-3).

The direct construction is theoretically useful but can be expensive for realistic dictionaries. The token alphabet grows with the dictionary, and a dense representation may contain a very large number of transitions. A compact construction based on delayed-input deterministic finite automata, default transitions, clean-copy reuse, and compressed reject transitions substantially reduces the representation size in practice [\[4,](#page-13-2) [7\]](#page-13-4).

The project, therefore, combines formal reasoning with substantial software engineering. Students shall implement the principal constructions, verify semantic equivalence against independent reference procedures, reproduce published examples, and conduct controlled experiments on state complexity, transition complexity, construction time, memory use, and tokenization throughput.

### **2.1 Main goals**

Beyond its technical content, the project is designed with the following main goals in mind:

- **An alternative route to demonstrating mastery.** A substantial part of the final course mark is earned through the project. Students who struggle with theory tests and examinations can therefore demonstrate their understanding of the course material through sustained, well-documented practical and analytical work, and can still pass the course (mostly) on the strength of that work.
- **A path towards formal publication.** Several of the extensions in Section [8](#page-7-0) address questions that are explicitly left open in the recent literature. A group whose project produces novel results may take the work further with the lecturer after the semester, with the aim of a formal publication.
- **A foundation for an honors project.** The implementations, experimental infrastructure, and open questions developed here form a natural starting point for an honours project, and interested students are encouraged to discuss this with the lecturer.
- **Experience with current research literature.** The project requires students to read, implement, and critically evaluate recent publications in the theory area, rather than only textbook material, and thereby to develop the skill of working directly from the research literature.

# **3 Project objectives**

On successful completion of the project, each group shall be able to:

- state and apply the formal definitions of a token alphabet, tokenization, proper BPE dictionary, token DFA, context-invariance, delayed-input DFA, and subsequential transducer [\[6,](#page-13-0) [5,](#page-13-1) [4,](#page-13-2) [3\]](#page-13-3);
- implement the successive-merge construction for a BPE tokenization DFA and justify the effect of each transformation on states, transitions, and accepted tokenizations [\[5\]](#page-13-1);
- implement a tokenizer based on finite-state transduction and compare its output with an independent BPE reference implementation [\[5,](#page-13-1) [3,](#page-13-3) [12\]](#page-13-5);
- implement the compact token-DFA construction and measure the reduction in explicit states or transitions relative to the baseline construction [\[4\]](#page-13-2);

- design tests that provide convincing evidence of correctness, including differential tests, exhaustive bounded tests, property-based tests, and negative tests;
- measure time and memory consumption reproducibly and interpret observed scaling in relation to the theoretical constructions;
- independently investigate one or more advanced extensions of the core material and report the outcome with appropriate rigour (Section [8\)](#page-7-0);
- communicate the design, correctness evidence, limitations, and results in a formal technical report, a live demonstration, and a recorded presentation.

# **4 Group organisation and technical requirements**

# **4.1 Group composition**

The project shall be completed in groups of exactly two students unless the lecturer grants written approval for a different arrangement. Both students are responsible for the complete submission and may be questioned on any component during the demonstration or oral discussion. The requirements are identical for CS345 and CS711 groups, with one exception: the number of advanced extensions, as specified in Section [8.](#page-7-0)

Students shall select their team members **within the first two weeks of the semester**. Once a group has been formed, one of the members shall email the names and student numbers of both members to the lecturer at [abvdm@sun.ac.za](mailto:abvdm@sun.ac.za).

# **4.2 Repository and development practice**

- The complete project shall be maintained in a Git repository on the **GitLab server of Computer Science**, created for this course under the account of either one of the two group members. GitLab repositories will be created in the first two weeks of the semester.
- The repository shall contain source code, automated tests, experiment scripts, configuration files, input dictionaries, generated summary data, the technical report, and a complete README.
- A clean checkout shall be executable by following the README.
- Randomised experiments shall use recorded random seeds.
- Generated automata may be displayed using Graphviz or an equivalent format, but a textual serialisation must also be available for automated testing.
- External code may be used only when its source, license, and role are clearly identified in the code and report.

## **4.3 Required internal representations**

The implementation shall separate the following concepts rather than represent all of them as unstructured strings:

- base symbols and tokens;
- ordered merge rules and dictionary priority;
- token sequences and their detokenized strings;
- DFA states, accepting states, and partial transitions;
- default transitions for delayed-input automata;

- transducer input transitions, emitted output, and final output;
- test fixtures and benchmark records.

### <span id="page-3-1"></span>**5 Compulsory technical tasks**

#### <span id="page-3-0"></span>**5.1 Formal dictionary model and independent reference tokenizer**

Implement a parser and validator for BPE dictionaries. The validator shall determine whether the dictionary is *proper* in the sense used by Berglund and van der Merwe: every non-base token used by a rule must have been constructed by a higher-priority rule [\[6,](#page-13-0) [5\]](#page-13-1). The implementation shall preserve the order of rules and shall report duplicate, malformed, unreachable, or unsupported entries rather than silently changing their meaning.

Implement a simple, independent reference tokenizer that follows the selected canonical BPE semantics directly. This implementation may be asymptotically slow; its purpose is to provide a transparent correctness oracle for small cases. For proper dictionaries, the SentencePiece-style and Hugging Face-style semantics considered by Berglund and van der Merwe coincide [\[6\]](#page-13-0).

### **5.2 Baseline BPE tokenization DFA**

Implement the successive-merge construction described in Algorithm 2 of Berglund, Martens and van der Merwe [\[5\]](#page-13-1). Starting with a string DFA over the base alphabet, apply each rule in dictionary-priority order to obtain a sequence of token DFAs *A*0*, A*1*, . . . , An*. The final automaton shall accept exactly the canonical tokenizations of the original language under the complete dictionary [\[5\]](#page-13-1).

The implementation shall support at least the universal one-state base DFA and user-supplied finite or regular base-language DFAs. For each merge *u* ≀ *v*, the code shall identify all relevant state triples, add transitions on *uv*, create and populate fresh states where required, redirect transitions on *u*, and preserve accepting-state status. The special case *u* = *v* shall be treated explicitly because it changes which inherited transitions are valid [\[5\]](#page-13-1).

**Required outputs.** For every construction run, produce a machine-readable record of the number of states, final states, tokens, transitions, and fresh states after each rule. Provide a deterministic textual serialisation and optional Graphviz output.

### **5.3 Reproduction and explanation of canonical examples**

Reproduce the principal small examples from the baseline token-DFA paper, including a case with *u* = *v*, a case with *u* ̸= *v*, and a chain of self-merges over a unary alphabet [\[5\]](#page-13-1). The report shall not merely include the final diagrams; it shall explain the state triples found, the fresh states created, the transitions removed or redirected, and the accepted tokenizations before and after each merge.

Add at least three original worked examples. At least one shall use non-ASCII symbols, and at least one shall use emoji or another multi-byte Unicode sequence. The implementation must state whether symbols are Unicode code points, bytes, or grapheme clusters; different choices are not interchangeable.

# **5.4 String-to-tokenization transducer**

Construct a finite-state transducer that maps input strings to their canonical tokenizations. The starting point shall be the token-DFA construction and the transducer ideas in Section 6 of Berglund, Martens and van der Merwe [\[5\]](#page-13-1). Where nondeterministic output behaviour arises, apply a correct determinisation or subsequentialisation method, drawing on the classical construction for functional transducers [\[3\]](#page-13-3).

The tokenizer shall be compared with the independent reference tokenizer from Section [5.1](#page-3-0) and, where compatible, with minbpe BasicTokenizer [\[12\]](#page-13-5). The comparison shall be made on token sequences, not only on detokenized text. Equality of detokenized text is necessary but does not establish equality of tokenization boundaries.

**Performance requirement.** Measure tokenization time and peak memory for the transducer tokenizer and at least one reference implementation. Interpret the results cautiously: a formally linear tokenizer may still have a large compiled state space, and practical pre-tokenization can alter the comparison [\[5,](#page-13-1) [13\]](#page-13-6).

#### **5.5 Compact delayed-input token automaton**

Implement the compact construction of Berglund, Jonsson, Martens, and van der Merwe [\[4\]](#page-13-2). The implementation shall support default transitions and shall make explicit which of the paper's optimisations are enabled. At minimum, the group shall implement the default-transition optimisation and the associated handling of reject or sink transitions. Implementing the stateavoidance and clean-copy-reuse optimisations is strongly recommended and will be assessed under completeness and performance.

The compact automaton shall be shown to be equivalent to the baseline automaton on all test instances for which both can be constructed. Equivalence shall be tested semantically through the extended transition function of the delayed-input automaton, not by comparing raw transition tables [\[4\]](#page-13-2).

**Required comparison.** For each dictionary prefix tested, report the baseline state count, baseline explicit transition count, compact state count, compact explicit transition count, defaulttransition count, construction time, and peak memory.

### **5.6 Larger-dictionary construction and controlled timeouts**

Apply the implementations to prefixes of at least two realistic BPE dictionaries, subject to available computing resources. Appropriate sources include GPT-2-style, Whisper-style, Phi-style, or other openly available merge lists [\[15\]](#page-13-7). Full construction is not compulsory when resource use becomes prohibitive. Instead, use increasing dictionary prefixes and record the largest prefix completed within fixed limits.

The experiments shall include a one-minute timeout and a ten-minute timeout, together with a stated memory limit. A timeout, memory exhaustion, or unsupported input is a result and shall be reported; it must not be omitted from tables or replaced by an unverified estimate.

# **6 Testing and verification requirements**

Testing is a principal project deliverable. The objective is not to accumulate a large number of superficial examples, but to combine independent forms of evidence that expose different classes of faults.

# **6.1 Deterministic unit and regression tests**

- **Empty dictionary:** the token DFA shall coincide with the base-token DFA.
- **No-op rule:** when no run reads *u* followed by *v*, applying *u* ≀ *v* shall not change the accepted language.

- **Fresh-state creation:** verify copied transitions, omitted transitions and accepting-state inheritance.
- **Self-merge** *u* = *v***:** verify left-to-right behaviour and confirm that invalid *uv* transitions are not inherited by a fresh state.
- **Distinct merge** *u* ̸= *v***:** verify that non-*v* outgoing transitions are preserved.
- **Loops and multiple incoming transitions:** verify redirection from every relevant predecessor.
- **Final and non-final intermediate states:** verify acceptance preservation.
- **Improper dictionary:** verify rejection or explicit diagnostic behaviour.
- **Useful and useless rules:** verify whether the rule changes any reachable behaviour.
- **Unicode and emoji alphabets:** verify that token identity is preserved without accidental byte or normalization changes.

### **6.2 Differential testing against an independent oracle**

For each test string *w*, compare the transducer output with the reference tokenization *TD*(*w*). The comparison shall verify all of the following:

- the output token sequence is identical;
- every output token belongs to the dictionary-induced token alphabet;
- concatenating the output tokens yields exactly *w*;
- the output token sequence is accepted by the constructed token DFA;
- deliberately altered token boundaries for the same underlying string are rejected whenever they are not canonical.

### **6.3 Exhaustive bounded testing**

For small alphabets and small proper dictionaries, enumerate every string up to a stated maximum length, for example all strings of length at most eight over {*a, b*}. Compare the reference tokenizer, transducer and token-DFA acceptance on every case. Where feasible, enumerate token sequences as well and verify that the DFA accepts exactly one tokenization for each underlying string in the tested bound. This is a particularly effective method for detecting subtle errors in fresh-state redirection and self-merges.

### **6.4 Property-based and fuzz testing**

Generate random small proper dictionaries and random strings using a fixed seed. A safe generator can build rules incrementally from tokens already present, thereby guaranteeing properness. At minimum, test the following properties:

- **detokenization:** *π*(*TD*(*w*)) = *w*;
- **stability:** tokenizing the detokenized canonical token sequence returns the same token sequence;
- **DFA agreement:** the canonical token sequence is accepted;
- **uniqueness within the tested bound:** no distinct accepted token sequence has the same detokenization;
- **baseline/compact agreement:** both automata return the same acceptance result;

- **reproducibility:** failures are logged with the dictionary, seed, input and smallest known counterexample.

### **6.5 Automata equivalence tests**

Use two complementary methods. First, compare the baseline and compact automata exhaustively on bounded token sequences. Second, where practical, expand the default transitions of the compact automaton and perform a product-automaton symmetric-difference emptiness check. Any limitations caused by large alphabets or partial transition functions shall be stated explicitly.

### **6.6 Pathological and robustness tests**

Recent streaming and incremental BPE work demonstrates that carefully structured inputs can expose latency or complexity weaknesses in common implementations [\[13,](#page-13-6) [11\]](#page-13-8). Include at least the following stress cases:

- repeated-character strings *a n* for increasing *n*;
- nested merge chains such as [*a* ≀ *a, aa* ≀ *aa, aaaa* ≀ *aaaa, . . .* ];
- long inputs without pre-tokenization boundaries;
- strings whose initial token changes after a later symbol is appended;
- mixed Unicode, combining marks, whitespace and emoji;
- malformed dictionaries and unsupported token encodings.

# **6.7 Test evidence in the submission**

The repository shall contain automated tests and a command that runs them. The report shall include a concise test matrix identifying each test family, the fault class it targets, the number of cases run, and the outcome. Screenshots are not a substitute for machine-readable test logs.

# <span id="page-6-0"></span>**7 Experimental evaluation**

# **7.1 Required measurements**

|              | Measurement |          | Required   | reporting      |            |            |             |             |             |                   |             |
|--------------|-------------|----------|------------|----------------|------------|------------|-------------|-------------|-------------|-------------------|-------------|
| Construction | time        |          | Wall-clock | time for       | each       | dictionary |             | prefix;     | report      | warm-up           | and repe   |
|              |             | tition   | policy.    |                |            |            |             |             |             |                   |             |
| Peak         | memory      |          | Maximum    | resident       |            | memory or  | a           | documented  |             | language-specific | equiv      |
| State        | count       |          | Reachable  | states,        | with       | sink       | states      | identified  | separately. |                   |             |
| Transition   | count       | Explicit |            | transitions;   |            | default    | transitions | shall       | be          | reported          | separately. |
| Tokenization | throughput  | Input    | bytes      | or             | characters | per        | second,     | with        | the unit    | stated.           |             |
| Output       | agreement   | Exact    |            | token-sequence |            | match      | rate        | against the | oracle.     |                   |             |
| Failure      | boundary    | Largest  |            | dictionary     | prefix     | or         | input size  | completed   | under       | each              | timeout     |
|              |             | and      | memory     | limit.         |            |            |             |             |             |                   |             |

### **7.2 Experimental method**

- Record the processor, memory, operating system, language version and important library versions.
- Separate automaton-construction time from serialisation and graph-rendering time.
- Use identical dictionary prefixes and language inputs when comparing implementations.
- Repeat short timing runs and report a robust summary, such as the median; do not average timeouts into successful measurements.
- Use logarithmic axes or separate plots when values differ by orders of magnitude.
- Provide raw CSV or JSON results in the repository and generate report tables or graphs from those files.
- Explain deviations from the algorithms in the cited papers and distinguish algorithmic changes from representation-level optimisations.

### **7.3 Minimum experimental questions**

- 1. How do state and transition counts grow with dictionary-prefix length for the baseline construction?
- 2. How much does the compact construction reduce explicit transitions and memory?
- 3. Which rule patterns create additional states, and which allow state reuse?
- 4. At what dictionary size does each construction reach the specified timeout or memory limit?
- 5. Does the transducer tokenizer agree exactly with the reference implementation on all comparable tests?
- 6. How does tokenization throughput change with input length on ordinary and pathological inputs?

# <span id="page-7-0"></span>**8 Advanced and bonus extensions**

The extensions in this section are not substitutes for the compulsory tasks in Sections [5–](#page-3-1)[7.](#page-6-0) Students are free to choose which extensions they undertake, subject to the following minimum requirements:

- **CS345 groups** shall complete **at least two** extensions from this section.
- **Groups containing a CS711 student** shall complete **at least three** extensions, of which at least one shall include a substantive formal component: a precise problem statement, a formal definition of the proposed extension, and either a proof, a counterexample, a complexity argument or a carefully designed experiment that answers a non-trivial research question.

Merely implementing an additional library feature does not satisfy these requirements. Groups undertaking work beyond the required minimum may earn bonus consideration. A group shall obtain approval from the lecturer before committing substantial time to an extension, and the chosen extensions shall be identified explicitly in the report and README.

#### **8.1 Tighter lookahead and delay bounds**

The early formalization of BPE proves the existence of finite sufficient lookahead but notes that the general bound is loose. It proposes a chain-length view of interacting rules and leaves the complexity and decidability of dictionary equivalence for future research [\[6\]](#page-13-0). Later streaming work defines transducer delay and gives computable upper bounds, but exact or substantially tighter bounds remain natural targets [\[13\]](#page-13-6).

A group may define an interference graph on merge rules, compute candidate chain parameters, compare these bounds with measured delay on small dictionaries, and search exhaustively for worst-case witnesses. A theory-focused submission should prove that the proposed bound is sound for a restricted dictionary class or provide a counterexample.

#### **8.2 Equivalence and canonicalisation of BPE dictionaries**

Two ordered dictionaries may induce the same tokenization function even when independent rules appear in a different order. Berglund and van der Merwe explicitly leave the decidability and complexity of dictionary equivalence as future research [\[6\]](#page-13-0). A tractable extension is to identify sufficient commutation conditions, construct a canonical partial order for small dictionaries, or implement bounded equivalence checking using the token DFAs and product constructions enabled by [\[5\]](#page-13-1).

#### **8.3 Symbolic automata for large token alphabets**

The token-DFA paper observes that practical base alphabets may involve Unicode and therefore create very large outgoing transition domains; it suggests symbolic automata as a possible representation [\[5\]](#page-13-1). An extension may replace explicit transition maps by predicates, intervals or equivalence classes and evaluate memory use. A theory component should specify when symbolic transition partitioning preserves context-invariance and determinism.

### **8.4 State complexity of subsequentialisation**

A functional tokenization transducer can be converted into an equivalent subsequential transducer, but the state complexity of this conversion deserves further analysis [\[5,](#page-13-1) [3\]](#page-13-3). Students may generate small dictionaries, construct the intermediate transducer, determinise it, minimise it, and seek families that exhibit rapid state growth. A theory submission may prove upper or lower bounds for a restricted family.

### **8.5 Further compact-state optimisations**

The compact construction prevents many redundant states and transitions, but the optimisation problem is not exhausted [\[4,](#page-13-2) [7\]](#page-13-4). Possible investigations include more aggressive clean-copy detection, post-construction state merging that respects default transitions, optimal or heuristic placement of default transitions, and direct symbolic encoding of reject transitions. Claims of improvement must be accompanied by equivalence tests and construction-cost measurements.

### **8.6 Partially ordered or DAG-structured dictionaries**

It is meaningful to investigate BPE dictionaries as directed acyclic graphs rather than as total orders, but this changes the semantics and must be treated as a research extension rather than a drop-in replacement. In standard BPE, the total rule order resolves conflicts. A DAG can encode two distinct relations: *dependencies*, stating that component tokens must be constructed before a rule can be used, and *priority constraints*, stating that one rule must precede another when their applications can interfere.

Multiple rules may be processed as one batch when they form an antichain and their effects commute. Disjoint applications are the simplest case. Difficulties arise when incomparable rules overlap, consume tokens produced by one another, or lead to different results under different topological orders. A deterministic semantics therefore requires one of the following: a tiebreaking rule; a confluence condition; or a restriction guaranteeing that all linear extensions of the DAG induce the same tokenization function.

A concrete theory extension is to characterise a class of partially ordered dictionaries for which all topological sorts are equivalent. A concrete implementation extension is to identify independent rule batches, apply their automaton transformations together, and compare the number of construction passes, time and resulting automaton size with the sequential algorithm. The key verification question is whether the batched automaton is equivalent to the automaton obtained from every permitted linear extension.

#### **8.7 Streaming and incremental tokenization**

Streaming BPE uses bounded transducer delay to emit stable tokens using memory independent of input length [\[13\]](#page-13-6). Incremental BPE maintains tokenizations of all prefixes and supports eager output with strong worst-case guarantees [\[11\]](#page-13-8). Extensions may compare these algorithms with the project transducer, implement chunked streaming, compute empirical delay, or investigate how pre-tokenization boundaries affect guarantees. The semantic output must remain exactly canonical.

### **8.8 Nondeterministic and stochastic tokenization**

BPE-dropout and related subword-regularisation methods deliberately allow multiple segmentations [\[16\]](#page-13-9). This breaks the unique canonical mapping used by context-invariant token DFAs. A theory extension may define the language of dropout-reachable tokenizations and ask whether it is regular, construct an NFA or weighted automaton for a restricted dropout model, or derive complexity bounds. An implementation may compare automaton-based sampling with a direct stochastic tokenizer.

### **8.9 BPE tokenizers for images and two-dimensional automata**

BPE-style merging has been applied to quantized visual tokens and to multidimensional data [\[18,](#page-14-1) [1\]](#page-13-10). Extending the token-DFA construction to images is a demanding extension: a fully general two-dimensional automaton model is substantially more difficult than the one-dimensional case, as the general theory of two-dimensional languages and automata makes clear [\[9,](#page-13-11) [10\]](#page-13-12). Therefore, groups should adopt a clearly restricted model. Consider looking at the work of Taylor Smith (and others) on two-dimensional automata theory.

A feasible progression is: (i) represent a quantized image as a rectangular grid over a finite alphabet; (ii) define horizontal and vertical merge rules for adjacent rectangular regions; (iii) restrict merges to axis-aligned rectangles; (iv) compare a row-major one-dimensional encoding with a genuinely two-dimensional rule application; and (v) construct a small recogniser or tilingstyle automaton for valid final segmentations. The report must distinguish an implemented restricted recogniser from a proof that the full two-dimensional tokenization language has a particular closure or decidability property.

Appropriate research questions include whether the merge order is confluent in a restricted 2D dictionary, whether a DAG of spatial dependencies provides a natural semantics, and whether the 1D context-invariance and state-complexity arguments have analogs for rectangular token regions. This extension may earn credit only after the compulsory 1D implementation and tests are complete.

#### **8.10 BPE tokenization of symbolic music**

BPE-style merging is not restricted to natural-language text. The MusicLang tokenizer applies BPE to symbolic (MIDI) music, merging frequently co-occurring musical events into larger tokens [\[14\]](#page-13-13); see <https://musiclang.github.io/tokenizer/>. An extension may extract the merge dictionary used by such a tokenizer, determine whether and under which encoding it forms a proper BPE dictionary in the sense of [\[6\]](#page-13-0), construct the corresponding token DFA or compact automaton for dictionary prefixes, and compare automaton-based tokenization with the library's own output on real MIDI data. Interesting questions include how the structure of musical merge rules, such as chords and repeated rhythmic patterns, affects state and transition growth compared with natural-language dictionaries, and whether musical pre-tokenization boundaries, such as bars and tracks, play the same role as whitespace pre-tokenization in text.

### **8.11 Pattern matching and constrained generation**

Token DFAs permit direct validation and pattern processing on canonical token sequences [\[5\]](#page-13-1). An extension may compose the token automaton with a DFA or Aho–Corasick matcher [\[2\]](#page-13-14), or investigate tokenization-aware constrained generation using a finite-state transducer [\[8\]](#page-13-15). Students shall compare direct token-level processing with detokenize-then-match baselines and shall test patterns that cross token boundaries.

# **9 Deliverables and submission requirements**

The complete project, **including the technical report**, shall be submitted on the **GitLab server of Computer Science**, in a repository created for this course under the account of one of the two group members, before **14:00 on Monday 5 October**. The state of the repository at the deadline constitutes the submission; commits after the deadline will not be considered.

| Deliverable              | Specification |              |              |               |                |                  |                     |
|--------------------------|---------------|--------------|--------------|---------------|----------------|------------------|---------------------|
| Source repository All    | source        | code,        | tests,       | scripts,      | configuration  | and              | licence/attribution |
| README                   | Installation, | execution,   | test         | and           | experiment     | instructions;    | repository          |
|                          | structure;    | known        | limitations; |               | identification | of the           | chosen advanced     |
| Technical report A       | formal        | PDF          | report of    | at least      | 10             | pages, excluding | references and      |
|                          | appendices,   | committed    | to           | the           | repository.    | There is         | no upper limit on   |
| the                      | number        | of pages.    |              |               |                |                  |                     |
| Automated test suite     | Runnable      | tests with   |              | deterministic | fixtures       | and recorded     | seeds.              |
| Experiment artefacts Raw | result        | files        | and scripts  |               | that           | regenerate the   | principal tables or |
| Recorded presentation A  | video         | presentation | of at        | least         | ten minutes.   | The report       | and README          |
| shall                    | contain       | a            | working link | to            | the video.     |                  |                     |
| Live demonstration A     | short         | executable   |              | demonstration | and            | oral discussion  | in which both       |
|                          | group         | members      | participate, | held          | for each       | group, one       | group at a time,    |
|                          | during the    | last three   | Monday       |               | tutorials      | of the semester. |                     |

### **9.1 Report structure**

The report shall be written as a technical document and shall contain, at a minimum:

- an introduction and precise statement of scope;

- formal definitions and cited algorithmic background;
- implementation architecture and data structures;
- a step-by-step explanation of the baseline and compact constructions;
- the transducer construction and determinisation strategy;
- testing methodology and evidence;
- experimental method, results, and interpretation;
- the chosen advanced extensions, with their motivation, method, and outcome;
- limitations, deviations from the literature, and unresolved issues;
- division of work between group members;
- a working hyperlink to the video presentation;
- a complete reference list.

## **9.2 Recorded presentation**

The recorded presentation shall not be shorter than ten minutes; there is no upper limit on its length, although clarity and focus are valued over length. It shall present the problem, the principal automata/transducer constructions, one concrete end-to-end example, the testing strategy, the main experimental results, at least one chosen extension, and the most important limitation. Both group members shall speak. The video shall be accessible to the markers for the complete marking period, and its link shall appear prominently in both the report and README.

### **9.3 Live demonstration and oral discussion**

The live demonstration and oral discussion will be conducted for each group, one group at a time, during the **last three Monday tutorials of the semester**. A schedule of time slots will be published in advance. Both group members shall participate and may be questioned on any component of the submission.

# **10 Assessment**

The project will be assessed out of 100 marks. Code that cannot be executed or meaningfully demonstrated cannot receive implementation marks for the affected component. Correctness claims unsupported by tests or reproducible evidence will receive limited credit. The advancedextension criterion is assessed against the minimum requirements of Section [8](#page-7-0) for the group's composition; work beyond the required minimum may earn bonus consideration at the lecturer's discretion.

Two components of the project deliberately carry no separate marks:

- The **formal dictionary model and independent reference tokenizer** (Section [5.1\)](#page-3-0) are not marked as a separate criterion. Instead, they are assessed through the role they play in demonstrating the correctness of the baseline token-DFA construction and of the tokenizer transducer. A weak or absent reference implementation will therefore reduce the correctness evidence, and hence the marks, for those two criteria.
- The **live demonstration and oral discussion** carry no separate marks. Instead, they are used, in addition to inspection of the code repository and the report, to evaluate all other criteria and to confirm that both group members understand the complete submission.

Marks for any criterion may be adjusted if a group member cannot explain or demonstrate the corresponding work.

| Criterion Marks Evidence                   | expected           |                   |              |
|--------------------------------------------|--------------------|-------------------|--------------|
| Baseline token-DFA construction 15 Correct | successive         | merges,           | special      |
| cases,                                     | example            | reproduction      | and          |
| explanation;                               | correctness        |                   |              |
| demonstrated                               | against            | the               | formal       |
| dictionary                                 | model              | and independent   |              |
| reference                                  | tokenizer          | of Section        | 5.1.         |
| Tokenizer transducer 15 Correct            | transduction,      |                   |              |
| behaviour;                                 | agreement          | with              | the          |
| independent                                | reference          | tokenizer         | of           |
| Section                                    | 5.1.               |                   |              |
| Compact delayed-input automaton 10 Correct | default-transition |                   | semantics,   |
| implemented                                | optimisations      |                   | and          |
| equivalence                                | evidence.          |                   |              |
| Testing and verification Unit,             | regression,        | exhaustive,       | fuzz,        |
| negative,                                  | equivalence        | and               | Unicode      |
| tests.                                     | Marks for          | this will         | be           |
| assigned                                   | at the             | other categories. |              |
| Experimental evaluation 10 Controlled      | measurements,      |                   | raw data,    |
| scaling                                    | analysis           | and honest        | failure      |
| Advanced extensions 15 Extensions          | completed          | to                | the          |
| required                                   | minimum            | for the           | group,       |
| with                                       | rigorous evidence  |                   | as specified |
| in Section                                 | 8.                 |                   |              |
| Software quality and README 10 Clear       | architecture,      | documentation,    |              |
| repeatable                                 | commands           | and               |              |
| Technical report 15 Formal                 | writing,           | correct           | citations,   |
| analysis,                                  | figures/tables     |                   | and          |
| Video presentation 10 Technical            | accuracy,          | clarity,          | concrete     |
| example,                                   | results            | and participation |              |
| by both                                    | students.          |                   |              |
| Total 100                                  |                    |                   |              |

# **11 Academic integrity and attribution**

The submission must represent the work and understanding of the two registered group members. Discussion of general concepts between groups is permitted, but source code, test suites, reports, figures, benchmark data , and recorded presentations may not be shared.

All external material shall be acknowledged. This includes copied or adapted code, algorithms, test cases, diagrams, datasets, software libraries, and generative-AI assistance. Attribution must appear where the material is used and in the reference list or README, as appropriate. The use of external code does not reduce the requirement that both students understand and can

explain the complete submission.

# **References**

<span id="page-13-15"></span><span id="page-13-14"></span><span id="page-13-13"></span><span id="page-13-12"></span><span id="page-13-11"></span><span id="page-13-10"></span><span id="page-13-9"></span><span id="page-13-8"></span><span id="page-13-7"></span><span id="page-13-6"></span><span id="page-13-5"></span><span id="page-13-4"></span><span id="page-13-3"></span><span id="page-13-2"></span><span id="page-13-1"></span><span id="page-13-0"></span>[1] Multidimensional byte pair encoding: Shortened sequences for improved visual data generation, 2024. arXiv:2411.10281. [2] Alfred V. Aho and Margaret J. Corasick. Efficient string matching: An aid to bibliographic search. *Communications of the ACM*, 18(6):333–340, 1975. [3] Marie-Pierre Béal and Olivier Carton. Determinization of transducers over finite and infinite words. *Theoretical Computer Science*, 289(1):225–251, 2002. [4] Martin Berglund, Anna Jonsson, Willeke Martens, and Brink van der Merwe. Constructing compact BPE token DFAs. In *Implementation and Application of Automata*, pages 27–40. Springer, 2025. [5] Martin Berglund, Willeke Martens, and Brink van der Merwe. Constructing a BPE tokenization DFA. *Theoretical Computer Science*, 1083:116131, 2026. [6] Martin Berglund and Brink van der Merwe. Formalizing BPE tokenization. *Electronic Proceedings in Theoretical Computer Science*, 388:16–27, 2023. [7] Philip Bille, Inge Li Gørtz, and Max Rishøj Pedersen. Fast practical compression of deterministic finite automata. In *SOFSEM 2025: Theory and Practice of Computer Science*, pages 136–150. Springer, 2025. [8] Marco Cognetta and Naoaki Okazaki. Tokenization as finite-state transduction, 2024. arXiv:2410.15696. [9] Dora Giammarresi and Antonio Restivo. Two-dimensional languages. In Grzegorz Rozenberg and Arto Salomaa, editors, *Handbook of Formal Languages, Volume 3: Beyond Words*, pages 215–267. Springer, 1997. [10] Katsushi Inoue and Itsuo Takanami. A survey of two-dimensional automata theory. *Information Sciences*, 55(1–3):99–121, 1991. [11] Shunyu Jiang and Ruiqi Gong. Incremental BPE tokenization. In *Proceedings of the 43rd International Conference on Machine Learning*, volume 306 of *Proceedings of Machine Learning Research*, 2026. arXiv:2605.30813. [12] Andrej Karpathy. minbpe: Minimal, clean code for the byte pair encoding algorithm used in LLM tokenization. GitHub repository. [13] Konstantinos Mamouras, Alexander W. Li, and Yifei Yang. An efficient algorithm for streaming BPE tokenization. *Proceedings of the ACM on Programming Languages*, 10(PLDI):article 252, 2026. [14] MusicLang. MusicLang tokenizer: BPE tokenization for symbolic music. Online documentation. [15] OpenAI. tiktoken: A fast BPE tokeniser for OpenAI models. GitHub repository. [16] Ivan Provilkov, Dmitrii Emelianenko, and Elena Voita. BPE-dropout: Simple and effective subword regularization. In *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*, pages 1882–1892, 2020.

<span id="page-14-1"></span><span id="page-14-0"></span>[17] Rico Sennrich, Barry Haddow, and Alexandra Birch. Neural machine translation of rare words with subword units. In *Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics*, pages 1715–1725, 2016. [18] Wanpeng Zhang, Zilong Xie, Yicheng Feng, Yijiang Li, Xingrun Xing, Sipeng Zheng, and Zongqing Lu. From pixels to tokens: Byte-pair encoding on quantized visual modalities, 2024. arXiv:2410.02155.