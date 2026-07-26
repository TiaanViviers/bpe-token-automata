# Incremental BPE Tokenization

Shenghu Jiang 1 2 Ruihao Gong 1 2

# Abstract

We propose a novel algorithm for incremental Byte Pair Encoding (BPE) tokenization. The algorithm processes each input byte in worst-case O(log<sup>2</sup> t) time, leading to an overall complexity of O(<sup>n</sup> log<sup>2</sup> t), where n is the input length and t is the maximum token length. The algorithm incrementally maintains BPE tokenization results for every prefix of the input text, implementing the standard BPE merge procedure defined by a fixed set of merge rules. This enables efficient partial tokenization in streaming settings. Functioning as a drop-in replacement for standard BPE, our approach achieves a speedup of up to ∼3× over Hugging Face's tokenizers, and demonstrates significant latency reductions over OpenAI's tiktoken on pathological inputs. We further introduce an eager output algorithm that enables streaming output, emitting tokens as soon as token boundaries are determined during incremental tokenization. Overall, our results demonstrate that BPE tokenization can be performed incrementally with strong worst-case guarantees, while providing practical latency benefits in modern large language model pipelines. The source code is available at [https://github.com](https://github.com/ModelTC/mtc-inc-bpe) [/ModelTC/mtc-inc-bpe](https://github.com/ModelTC/mtc-inc-bpe).

## 1. Introduction

Byte Pair Encoding (BPE), originally proposed as a data compression technique by [Gage](#page-9-0) [\(1994\)](#page-9-0), has become the de facto tokenization method for modern large language models (LLMs) following its adaptation by [Sennrich et al.](#page-10-0) [\(2016\)](#page-10-0). By iteratively merging frequent adjacent symbol pairs, BPE constructs a compact vocabulary that balances expressiveness with computational efficiency. Consequently, highly optimized implementations such as Hugging

Face's tokenizers [\(Hugging Face,](#page-9-1) [2026\)](#page-9-1) and OpenAI's tiktoken [\(OpenAI,](#page-9-2) [2026b\)](#page-9-2) have become standard components in modern LLM pipelines.

Figure [1](#page-0-0) illustrates a representative pipeline used in modern LLM tokenization, where BPE is applied as a core stage within a broader sequence of preprocessing steps.

<span id="page-0-0"></span>![](_page_0_Diagram_9.jpeg)

*Figure 1.* A representative pipeline in modern LLM tokenization. Raw text is processed by a sequence of model-specific preprocessing stages before applying BPE tokenization to each resulting chunk. *Our work focuses on making the BPE stage incremental without altering the correctness and the surrounding stages.*

However, these tools are predominantly designed as offline processes: they require the entire input sequence (or a presegmented chunk) to be fully observed before producing a canonical tokenization. As a result, tokenization and prefilling are executed sequentially rather than concurrently, which introduces additional latency in streaming and longcontext inference.

At an algorithmic level, existing implementations typically rely on heap-based priority queues to select merges over the full input, leading to a formulation that is inherently global and difficult to adapt to byte-by-byte updates. The formalization of BPE by [Berglund & van der Merwe](#page-8-0) [\(2023\)](#page-8-0) implies a structural property where the tokenizations for every prefix of a text form a prefix tree of tokens. This property suggests the possibility of immediate feedback and partial processing; however, exploiting it efficiently requires algorithmic support beyond standard implementations.

In this paper, we present a novel algorithm for incremental BPE tokenization that efficiently maintains BPE tokenizations for every prefix in real-time. Our algorithm processes each input byte in a worst-case time complex-

Email: Shenghu Jiang <[research@chielo.org](mailto:research@chielo.org)>. <sup>1</sup>Beihang University <sup>2</sup> SenseTime Research. Correspondence to: Ruihao Gong <[gongruihao@buaa.edu.cn](mailto:gongruihao@buaa.edu.cn)>.

*Proceedings of the* 43 rd *International Conference on Machine Learning*, Seoul, South Korea. PMLR 306, 2026. Copyright 2026 by the author(s).

ity of O(log<sup>2</sup> t), resulting in an overall time complexity of O(<sup>n</sup> log<sup>2</sup> t), where n is the input length and t is the maximum token length.

We implement the algorithm in Rust as a drop-in replacement for core BPE stages. Benchmark results (Table [1\)](#page-7-0) show an end-to-end speedup of up to ∼3× over Hugging Face's tokenizers. Furthermore, while existing tools like OpenAI's tiktoken exhibit O(<sup>n</sup> 2 ) behavior on certain inputs, our approach maintains a stable O(<sup>n</sup> log<sup>2</sup> t) cost, leading to significant latency reductions on pathological cases (Figure [3\)](#page-7-1).

Beyond raw speed and streaming input, we introduce an *eager output* mechanism for streaming output, which emits tokens as soon as stable token boundaries are resolved. This enables tokenization to be fully pipelined with model inference.

Profiling of current systems (Appendix [I\)](#page-26-0) shows that stages other than BPE can become bottlenecks in tokenization pipelines, burdening both streaming input and output. With strict worst-case complexity guarantees, such presegmentation can be algorithmically redundant.

Furthermore, along with incremental updates, the algorithm naturally supports scenarios requiring full-prefix access, i.e., scenarios in which tokenizations of all prefixes are required, such as deriving attention masks from the prefix tree of tokens for "fill-in-the-middle" (FIM) tasks without random or heuristic truncation and re-computation.

Our results demonstrate that incremental BPE tokenization is both algorithmically feasible and practically beneficial, with strict worst-case guarantees and exact semantic compatibility.

Contributions. We make the following contributions:

- An incremental BPE algorithm is proposed with a strict worst-case O(log<sup>2</sup>
  - t) per-byte complexity, ensuring exact equivalence with standard BPE alongside rigorous performance guarantees.
- The proposed eager output mechanism enables efficient, real-time streaming and pipelining with model inference.
- Our efficient implementation in Rust serves as a drop-in replacement that delivers a speedup of up to ∼3× over current state-of-the-art tools.
- With our method, stages of traditional pipelines that serve solely to circumvent the limits of global BPE can be safely removed without performance concerns.
- Our method provides native support for full-prefix tasks (e.g., FIM, token healing) by efficiently providing tokenizations of all prefixes, eliminating the need for heuristic truncation or re-computation.

## 2. Related Work

Byte Pair Encoding [\(Sennrich et al.,](#page-10-0) [2016\)](#page-10-0) has established itself as the de facto standard for modern LLMs, employed by state-of-the-art architectures such as GPT-5 [\(OpenAI,](#page-9-3) [2026a\)](#page-9-3) and Qwen-3 [\(Qwen Team,](#page-10-1) [2025a\)](#page-10-1). Despite alternatives like WordPiece [\(Schuster & Nakajima,](#page-10-2) [2012\)](#page-10-2) used in BERT [\(Devlin et al.,](#page-9-4) [2019\)](#page-9-4) and Unigram [\(Kudo,](#page-9-5) [2018\)](#page-9-5) adopted by T5 [\(Raffel et al.,](#page-10-3) [2020\)](#page-10-3), BPE remains the predominant choice for current models.

In terms of model architecture, usage patterns have evolved: while earlier models typically applied BPE to the unsegmented input text, modern LLMs increasingly adopt regexbased pre-segmentation and other normalization to enforce linguistic boundaries and partition the input.

Leading libraries implement these strategies differently: Hugging Face's tokenizers [\(Hugging Face,](#page-9-1) [2026\)](#page-9-1) provides a general-purpose implementation using priority queues, whereas OpenAI's tiktoken [\(OpenAI,](#page-9-2) [2026b\)](#page-9-2) specializes in the regex-based approach, relying on segmentation to bound the cost of BPE merges.

Despite these optimizations, production-grade tokenization remains predominantly *offline*. Whether relying on global queues or pre-segmentation, canonical BPE tokenization is typically performed after a complete segment is available.

This architecture restricts the ability to hide latency by pipelining tokenization with model inference at a finegrained level. Furthermore, the reliance on regex engines for complexity control can be brittle, potentially introducing performance degradation or stack exhaustion on pathological inputs such as extensive repetitions.

On the theoretical side, [Berglund & van der Merwe](#page-8-0) [\(2023\)](#page-8-0) analyze the formal semantics of different BPE implementations and note its consistency under token-wise truncation. This observation implies that the tokenization of a string prefix remains stable within the full tokenization, hinting at the possibility of incremental processing. However, their work focuses on algebraic properties rather than algorithmic construction, and does not address the challenge of bounding the lookahead required for online updates.

In the engineering domain, practical implementations such as the crate bpe in rust-gems [\(GitHub,](#page-9-6) [2026\)](#page-9-6), whose techniques are discussed by [van Antwerpen & Neubeck](#page-10-4) [\(2024\)](#page-10-4), have adopted the Aho–Corasick automaton [\(Aho &](#page-8-1) [Corasick,](#page-8-1) [1975\)](#page-8-1) for incremental tokenization. The detailed comparison is discussed in Appendix [J.](#page-27-0) While demonstrating practical utility, these approaches generally lack formal worst-case complexity guarantees.

Our work bridges this gap by providing an incremental algorithm with O(log<sup>2</sup> t) worst-case update time while maintaining strict compatibility with standard BPE.

### 3. Structural Foundations of Incremental BPE

In this section, we establish the structural foundations of our algorithm. We first formalize the incremental tokenization problem by explicitly defining the concept of the Last Token and deriving the recursive properties of BPE. We then introduce a normalized representation of the BPE vocabulary to eliminate redundancy. Finally, we construct the Successor Forest and the Suffix-Successor Tree, which organize the search space for incremental tokenization. These structures provide the topological basis for the theoretical properties and search algorithms presented in subsequent sections.

### <span id="page-2-1"></span>3.1. Preliminaries and Definitions

Let <sup>Σ</sup> be a finite alphabet and <sup>V</sup> ⊂ <sup>Σ</sup> <sup>+</sup> be a finite vocabulary. The vocabulary <sup>V</sup> consists of atomic tokens (where |t| = 1) and non-atomic tokens (where |t| <sup>&</sup>gt; <sup>1</sup>).

<sup>A</sup> suffix token of a string <sup>s</sup> is defined as any token <sup>t</sup> ∈ <sup>V</sup> that is a suffix of s.

A token sequence φ = [t1, . . . , tn] maps back to the string via detokenization π(φ) = t<sup>1</sup> . . . tn.

A dictionary is defined by an ordered list of merge rules D = [r1, r2, . . . , rm]. Each rule r<sup>i</sup> specifies a pair of adjacent tokens (x, y) to be merged into a new token z = xy.

Applying a rule r to a token sequence φ, denoted as Tr(φ), replaces occurrences of adjacent tokens x and y with z sequentially from left to right.

The full BPE tokenization for a string s with the dictionary D, denoted as TD(s), is obtained by initially mapping s to a sequence of characters φ0, and then applying the rules in D according to their priority:

$$\mathbb{T}_D(s) = (\mathbb{T}_{r_m} \circ \cdots \circ \mathbb{T}_{r_2} \circ \mathbb{T}_{r_1})(\varphi_0) \quad (1)$$

where r<sup>1</sup> represents the highest priority rule.

Note that under this definition, the standard BPE differs from the SentencePiece [\(Kudo & Richardson,](#page-9-7) [2018\)](#page-9-7) semantics. Our analysis is formulated under the standard BPE merge semantics. See Appendix [A](#page-11-0) for a detailed discussion on the difference between the two tokenization semantics and the method to "properize" merge rules for the standard BPE.

In the remainder of this paper, we omit the subscript D and write T(s) when the dictionary is clear from context.

## 3.2. Problem Formulation

Prefix Consistency. Our incremental approach relies on the consistency of BPE tokenization under token-wise truncation. As noted by [Berglund & van der Merwe](#page-8-0) [\(2023\)](#page-8-0)

(Remark 3), a valid BPE tokenization T(·) can be freely truncated: the remaining sequence remains the valid tokenization of its corresponding substring.

<span id="page-2-0"></span>Lemma 3.1 (Prefix Consistency). *Let* s *be a string and* φ = T(s) *be its token sequence after tokenization. For any proper prefix* <sup>µ</sup> ⊂ <sup>φ</sup> *of the token sequence, the following identity holds:* T (π (µ)) = µ*.*

Intuitively, this lemma holds because each BPE merge step is a boundary elimination process visualized in Figure [4.](#page-14-0) We provide an independent formal proof in Appendix [B.](#page-13-0)

This lemma ensures that the tokenization of a growing string can be modeled as extending the previous valid tokenization of some shorter prefix rather than re-computing from scratch.

The Last Token. Based on this consistency, we define the Last Token, denoted as θ(s). For any non-empty string s, θ(s) is the last token in its BPE tokenization sequence: θ(s) = last (T (s)).

According to the Prefix Consistency lemma (Lemma [3.1\)](#page-2-0), since removing the last token leaves a valid tokenization sequence for the remaining string prefix, we can express the tokenization recursively:

T(s) = T (spre) ⊕ [<sup>θ</sup> (s)] (2)

where spre is the string s with the suffix string of θ(s) removed, and ⊕ denotes sequence concatenation.

In terms of complexity, the full-prefix tokenization requires maintaining Θ(|s|) states.

Prefix Tree of Tokens. This recursive relationship implies that the tokenizations of all prefixes naturally form a hierarchical structure. Strictly speaking, this structure constitutes a forest, as a tokenization sequence may begin with any valid token. To unify this into a single Prefix Tree of Tokens, we introduce a virtual root representing the tokenization of the empty string ε, which serves as the shared root for all initial tokens.

While we visualize the space of all prefix tokenizations as this tree, strictly maintaining the explicit structure is unnecessary. Instead, the tokenization for any prefix can be retrieved solely by *backtracking* using <sup>θ</sup>(·) until the beginning of the string (the virtual root) is reached.

Incremental Objective. Consider an incremental scenario where a character c is appended to the current string s, resulting in s ′ = sc. To update the tokenization, we only need to find the value of θ(s ′ ). The objective is to identify θ(s ′ ) within the *intersection* of the set of all suffixes of s ′ and the vocabulary V . In the following sections, we introduce the

Successor Forest and other structures to efficiently solve this search problem.

### <span id="page-3-1"></span>3.3. Normalization and Token Hierarchy

In practice, BPE vocabularies often contain unreachable entries. To facilitate efficient updates, we define a normalized representation. We say a token <sup>t</sup> ∈ <sup>V</sup> is canonical if TD(t) = [t]. The normalized vocabulary V consists solely of canonical tokens. Crucially, the determinism of BPE establishes a bijective mapping between non-atomic canonical tokens and the specific merge rules that produce them, which we term canonical rules. The normalized dictionary D contains strictly these rules. We show in Appendix [C](#page-14-1) that this normalization preserves exact compatibility, i.e., TD(s) ≡ TD(s).

Predecessors and Successors. Based on the bijection above, for every non-atomic <sup>t</sup> ∈ V produced by the canonical rule (x, y) of t, we define its predecessor pre(t) = x and successor suc(t) = y. As detailed in Appendix [C,](#page-14-1) the determinism of BPE ensures x, y ∈ V. Thus, the vocabulary is closed under these operations, forming the topological basis for the Successor Forest.

### 3.4. Successor Forest

Based on the hierarchy, we construct the topological structure for searching <sup>θ</sup>(·). We define the Successor Forest (Fsuc) as a directed graph <sup>G</sup> = (V, E) where edges point from a token to its successor: <sup>E</sup> <sup>=</sup> {(u,suc(u)) | <sup>u</sup> ∈ V, |u| <sup>&</sup>gt; <sup>1</sup>}. Since edges strictly reduce token length (|suc(u)| <sup>&</sup>lt; |u|), <sup>G</sup> is acyclic and forms a forest of trees rooted at atomic tokens.

An example Successor Forest is illustrated in Figure [2.](#page-4-0)

## 3.5. Suffix-Successor Tree

By definition, for any non-atomic token u, u = pre(u) suc(u), which implies suc(u) is a proper suffix of <sup>u</sup>. This property ensures that traversing parents in Fsuc corresponds to taking proper suffixes.

For a given token <sup>t</sup> ∈ V, we define the Suffix-Successor Tree, denoted as SufSucTree(t), as the subgraph of Fsuc induced by the set of all canonical tokens that are suffixes of t.

Let <sup>S</sup><sup>t</sup> be the set of suffix tokens of <sup>t</sup> (note that <sup>t</sup> ∈ <sup>S</sup>t). If a non-atomic token <sup>u</sup> ∈ <sup>S</sup>t, then its parent in the forest, suc(u), must also be a suffix of <sup>t</sup>, implying suc(u) ∈ <sup>S</sup>t. Since all suffixes of t share the same last character, all paths in this subgraph converge to the unique atomic suffix token of t. Therefore, SufSucTree(t) forms a single tree rooted at this atomic token.

This structure organizes all potential candidates for the value of <sup>θ</sup>(·). By identifying further properties on this tree, we can reformulate the incremental tokenization as an efficient tree search problem.

An example Suffix-Successor Tree is highlighted in violet in Figure [2.](#page-4-0)

## 4. The Monotonic Path Property

This section establishes the key property underlying BPE for suffix tokens. For any input string, we will show that the suffix tokens capable of serving as the final token form a single monotonic path in the Suffix-Successor Tree.

### <span id="page-3-2"></span>4.1. Intuition

Fix a non-empty string s and a suffix token t of s. For t to be the valid last token θ(s), the boundaries around its components pre(t) and suc(t) are required to survive the merge process before applying the canonical rule of t (as formalized in Lemma [E.3](#page-16-0) and Lemma [E.6\)](#page-16-1).

This survival establishes a necessary dual constraint on the merge history:

- 1. Structural Reachability: pre(t) must appear as the rightmost token at some stage during the processing of the prefix, meaning the eventual last token of the prefix must be a descendant of pre(t).
- 2. Procedural Priority: The merge rule forming t must execute *before* any rule that would otherwise consume pre(t) (specifically, merging it with a left neighbor).

Crucially, these conditions are necessary but not sufficient, since the newly formed token t may still be involved in subsequent merges before the final tokenization is reached.

Another intuition is that the rightmost token can be viewed as evolving through the tokenization: starting from an atomic token, it is progressively merged with its adjacent token. This process can be viewed as traversing a descendant path in the Successor Forest, until reaching the last token of the final tokenization.

We provide a detailed derivation of this intuition based on the "boundary elimination" logic in Appendix [D.](#page-14-2)

## 4.2. Formalization

We now formalize the intuition from the previous subsection. The following definition establishes a rigorous criterion for determining whether a candidate suffix token t is compatible with the tokenization of the remaining prefix.

<span id="page-3-0"></span>Definition 4.1 (Prefix Last-Token Condition). Fix a nonempty string s and a suffix token t of s.

<span id="page-4-0"></span>![](_page_4_Diagram_2.jpeg)

*Figure 2.* Successor Forest and the merge rules. Solid edges denote the Successor Forest, while dashed edges indicate predecessors. Violet nodes highlight SufSucTree(abcdef). Other colored nodes, formed by the predecessors and some of their subtrees, identify the tokens θ(s − suc(t) ) satisfying the Prefix Last-Token Condition (Definition [4.1\)](#page-3-0) for the tokens t: ef, def, bcdef, and abcdef.

If t is an atomic token, it satisfies the Prefix Last-Token Condition by definition.

If t is a non-atomic token, let s <sup>−</sup> suc(t) denote the prefix obtained by removing the suffix suc(t) from s. We say that t satisfies the condition with respect to s if the following hold:

- 1. Reachability. The token θ(s − suc(t) ) lies in the subtree of the Successor Forest rooted at pre(t) (including the case θ(s − suc(t) ) = pre(t)).
- 2. Priority dominance. If θ(s − suc(t) ) ̸= pre(t), let <sup>u</sup> be the unique child of pre(t) that lies on the ancestor path from θ(s − suc(t) ) to pre(t). Then the canonical rule of t has strictly higher priority than that of u.

We now assert the main structural theorem of this paper.

<span id="page-4-1"></span>Theorem 4.2 (Monotonic Path Property). *Let* k *be the longest canonical suffix token of a string* s*. Consider the Suffix-Successor Tree* SufSucTree(k)*. Let* P *denote the unique path from the last token* θ(s) *to the root. Then a node* <sup>t</sup> ∈ SufSucTree(k) *satisfies the Prefix Last-Token Condition if and only if* t *lies on the unique path* P*.*

We provide the complete proof in Appendix [E.](#page-15-0) The "if" direction follows directly from the intuition above: along the successor chain of the true last token, both reachability and priority dominance are preserved monotonically.

It is notable that, although the Monotonic Path Property restricts the search space to the Suffix-Successor Tree of the longest suffix token, *the Prefix Last-Token Condition itself is evaluated in the global Successor Forest*. In particular, for a candidate token t, the condition depends only on the relative position between pre(t) and θ(s − suc(t) ) in the Successor Forest, and does not depend on the membership of pre(t) in SufSucTree(t).

## <span id="page-4-2"></span>4.3. Linearization via DFS

To utilize the Monotonic Path Property to find the last token θ(s), it requires an efficient method to verify whether a node <sup>t</sup> ∈ SufSucTree(k) satisfies the Prefix Last-Token Condition (Definition [4.1\)](#page-3-0).

For a fixed non-atomic token t, consider the possible values of θ(s − suc(t) ) that satisfy the condition. This set of valid tokens forms the subtree rooted at pre(t) in the Successor Forest dictated by the "Reachability" requirement, excluding the subtrees rooted at any direct child of pre(t) whose canonical rule has a priority greater than or equal to that of t, as enforced by the "Priority dominance".

Let C<sup>t</sup> be the set described above for a non-atomic token <sup>t</sup>. If <sup>t</sup> is an atomic token, C<sup>t</sup> is simply defined as an empty set. In this section, we show that membership in C<sup>t</sup> can be evaluated in O(1) time with DFS linearization.

DFS Linearization of the Successor Forest. To linearize the forest topology, we perform a pre-order Depth-First Search (DFS) starting from the atomic tokens. We maintain a global counter that increments exactly once upon entering each node u, assigning it a unique entry timestamp dfs in(u). We then assign an exit timestamp dfs out(u) immediately after fully exploring its subtree.

This process establishes a bijection between the nodes and the timestamps. Crucially, it guarantees that the subtree rooted at any node u corresponds exactly to a contiguous half-open interval [dfs in(u), dfs out(u)).

Additionally, when traversing the children of a node u, we visit them in strictly increasing order of their canonical rule priorities (from lowest to highest priority). This deliberate ordering ensures that children with lower priorities are mapped to earlier timestamps, enabling us to efficiently exclude the subtrees of higher-priority children to enforce the "Priority dominance" condition.

Valid Interval. Notably, the set C<sup>t</sup> corresponds to a contiguous range of timestamps. For each non-atomic canonical token t, we precompute a *valid interval* I<sup>t</sup> = [Lt, Rt) such that a node <sup>x</sup> ∈ C<sup>t</sup> if and only if dfs in(x) ∈ <sup>I</sup>t. Concretely:

- L<sup>t</sup> = dfs in(pre(t));

- R<sup>t</sup> = dfs in(u), where u is the first child of pre(t) (in the DFS traversal order) whose canonical rule priority is greater than or equal to that of t. If no such child exists, we set R<sup>t</sup> = dfs out(pre(t)).

The construction above reduces the evaluation of the Prefix Last-Token Condition to an O(1) interval membership test.

Mutual Exclusion among Siblings. Finally, it is notable that the valid intervals of sibling nodes in the Suffix-Successor Tree are necessarily disjoint. This is a direct corollary of the Monotonic Path Property (Theorem [4.2\)](#page-4-1). If the intervals of two distinct siblings overlapped, there would exist a prefix state for which both siblings satisfy the Prefix Last-Token Condition, implying the existence of valid nodes on two diverging branches. This contradicts the uniqueness of the valid path guaranteed by Theorem [4.2.](#page-4-1)

Thus, for any two distinct children u and v of a node, we have <sup>I</sup><sup>u</sup> ∩ <sup>I</sup><sup>v</sup> <sup>=</sup> ∅. This mutual exclusion enables the search algorithm to unambiguously identify the correct branch at each step.

## 5. Incremental Algorithm

Based on the theoretical foundations established in the previous sections, we now present the incremental algorithm for maintaining the last token θ(s). In this section, we first outline the abstract algorithmic framework and its design objectives. We then detail the specific data structures, the Aho– Corasick automaton [\(Aho & Corasick,](#page-8-1) [1975\)](#page-8-1) and Centroid Decomposition, employed to implement each component efficiently.

### 5.1. Algorithm Framework

The incremental update problem can be framed as follows: given the current string s, its last token θ(s), and a new character c, we aim to compute the new last token θ(sc).

Our strategy relies on the structural properties of the search space. First, recall that θ(sc) must be a suffix token of the string sc. While there may be many suffix tokens, they are all suffixes of the longest suffix token, denoted as τ (sc). Consequently, the Suffix-Successor Tree SufSucTree(τ (sc)) defines our search space.

Within this search space, the Monotonic Path Property (Theorem [4.2\)](#page-4-1) guarantees that the set of nodes satisfying the Prefix Last-Token Condition forms a single continuous path anchored at the root (the atomic token c). Since the atomic token is always a valid candidate, this path is never empty. The correct last token θ(sc) corresponds to the deepest node of this valid path.

Therefore, the algorithm proceeds in two abstract steps:

- 1. Search Space Identification: Identify the longest suffix token τ (sc) to determine the bounding tree SufSucTree(τ (sc)).
- 2. Path Extension Search: Within SufSucTree(τ (sc)), search for the deepest node satisfying the Prefix Last-Token Condition.

To evaluate the Prefix Last-Token Condition during the search, the algorithm requires access to the last tokens of previous prefixes. We abstract this as a history interface H(ℓ), which returns the last token of the prefix obtained by removing ℓ characters from the end of the current string.

### 5.2. Search Space Maintenance via Aho–Corasick Automaton

To identify τ (sc), we maintain an Aho–Corasick automaton [\(Aho & Corasick,](#page-8-1) [1975\)](#page-8-1) on V. We augment the structure by precomputing the search space entry point: for each state <sup>u</sup>, the annotation is the token <sup>u</sup> itself if <sup>u</sup> ∈ V, otherwise it is inherited from u's suffix link. This allows retrieving <sup>τ</sup> (sc) in O(1) without traversing suffix links. We store the transition table using a persistent square-root tiling (details in Appendix [F\)](#page-20-0) to ensure O(1) transition queries with memory efficiency. The annotation at the new state identifies the specific SufSucTree(·) for the subsequent search.

## 5.3. Efficient Search via Centroid Decomposition

The main challenge is to efficiently locate the deepest valid node within SufSucTree(τ ), where τ = τ (sc). Since the tree height can be linear in |<sup>τ</sup> |, a naive top-down traversal is inefficient. We solve this by guiding the search using Centroid Decomposition.

For each canonical token <sup>τ</sup> ∈ V, we precompute a Centroid Search Tree (CST). The CST is a tree of height O(log |<sup>τ</sup> |), where each node corresponds to a centroid u of a weak component in the recursive decomposition of SufSucTree(τ ). Crucially, from the perspective of a centroid u, the original tree is split into disjoint weakly connected components: one component containing the parent of u (the "upward" direction), and several components each containing a child of u (the "downward" directions).

The search for θ(sc) proceeds by traversing this CST. At each step, let u be the current centroid. We evaluate the Prefix Last-Token Condition for u by querying the history state <sup>k</sup> <sup>=</sup> H(|suc(u)|) and performing the interval check dfs in(k) ∈ <sup>I</sup>u. Based on the Monotonic Path Property, we determine the direction of the valid path's endpoint:

- 1. Case 1: <sup>u</sup> is invalid (dfs in(k) ∈/ <sup>I</sup>u). Since the valid path is anchored at the tree root (the atomic token), an invalid node u implies that the path does not in-

tersect with the subtree of SufSucTree(τ ) rooted at u; i.e., the path must be inside the component of the parent. We transition to the CST child corresponding to the component containing u's parent (the upward direction).

- 2. Case 2: <sup>u</sup> is valid (dfs in(k) ∈ <sup>I</sup>u). The node <sup>u</sup> lies on the valid path. The target θ(sc) is either u itself or its descendant. To determine if the path extends deeper, we check the children of u in the original SufSucTree(τ ). Recall from Section [4.3](#page-4-2) that the valid intervals of siblings are disjoint. We can thus pre-sort the intervals and perform a binary search over the children to check if any child v is valid.
  - If a valid child <sup>v</sup> exists (i.e., dfs in(H(|u|)) ∈ <sup>I</sup>v), the path continues into v's subtree. We transition to the CST child corresponding to the component containing v.
  - If no child is valid, then the path ends at u. We conclude θ(sc) = u and terminate the search.

### 5.4. Complexity Analysis

The worst-case time complexity per byte is dominated by the centroid search.

- Automaton State Update: The optimized automaton transition takes O(1) time.
- CST Traversal: The CST height is bounded by O(log |<sup>τ</sup> |).
- Decision Step: At each CST node, we perform either a single interval check or a binary search over the children. Since the degree of a node in SufSucTree(τ ) is bounded by |<sup>τ</sup> |, the binary search takes O(log |<sup>τ</sup> |).

Each check involves a history query H(·), assumed to be an O(1) operation. Combining these factors, the complexity per byte is O(log<sup>2</sup> |<sup>τ</sup> |), leading to an overall complexity of O(<sup>n</sup> log<sup>2</sup> t) for the entire input, where t is the maximum token length.

## <span id="page-6-0"></span>6. Eager Output

The incremental algorithm efficiently maintains the state θ(s). Since the sequence of last tokens implicitly encodes the *Prefix Tree of Tokens*, the full tokenization is typically recovered by backtracking from θ(s) to the virtual root.

In a streaming setting, however, incrementality alone does not guarantee streaming output. Thus, the challenge is to identify the initial segment of this backtracking chain that has become invariant, serving as the common ancestry for any future extension of the string.

### <span id="page-6-1"></span>6.1. The Active Frontier

The ambiguity of the output stream arises from the uncertainty of which current node in the Prefix Tree of Tokens will serve as the parent for future tokens. When new characters are appended to s, any newly formed last token must attach to the last token of some prefix of s.

The range of such possible attachments is bounded by the maximum suffix length queried during the incremental search, which corresponds to the deepest state reached in the Aho–Corasick automaton. Let d(s) be the depth of the state reached by the string s in the Aho–Corasick automaton. Note that this depth corresponds exactly to the length of the longest suffix of s recognized by the automaton. Since any future token formed must be recognized by the automaton, its length cannot exceed d(s).

Consequently, the parent of any future token must be the last token of a prefix ending in the interval [|s| − <sup>d</sup>(s), |s|].

We thus define the set of Parental Candidates, P, as the set of all last tokens that fall within this interval:

$$\mathcal{P} = \{\theta(s[1 \dots i]) \mid |s| - d(s) \leq i \leq |s|\}$$
 (3)

where s[1 . . . 0] indicates the empty string ε and θ(ε) is the virtual root of the Prefix Tree of Tokens. The stable output is the common ancestral path shared by all tokens in P.

### 6.2. Maintenance Algorithm

To efficiently identify and emit the stable tokens, we exploit the monotonicity of the window boundaries. Observe that the automaton transition for a new character can increase the state depth by at most 1 (i.e., <sup>d</sup>(sc) ≤ <sup>d</sup>(s) + 1). Therefore, the start of the window, |s| − <sup>d</sup>(s), is monotonically nondecreasing. This guarantees that candidates only "expire" from P as the window slides forward; previously expired tokens never re-enter.

Based on this property, we implement a two-pointer algorithm to maintain the set P and track the active subgraph in the Prefix Tree of Tokens. Tokens are emitted eagerly once all active paths converge to a single child of the virtual root. The detailed algorithmic steps and complexity analysis are provided in Appendix [G.](#page-21-0)

While eager output enables streaming, it introduces computational overhead due to maintaining the dynamic subgraph. Therefore, unless otherwise specified, the standard benchmarks presented later utilize the non-eager incremental algorithm.

## 7. Benchmarks

We evaluate the end-to-end throughput of our incremental BPE algorithm by integrating it as a drop-in replace-

<span id="page-7-1"></span>![](_page_7_Figure_1.jpeg)

*Figure 3.* End-to-end throughput under pathological inputs (log–log scale). Filled markers represent measured results, while hollow markers indicate extrapolated values beyond the measurable range. The dashed vertical line highlights the input length at which the regular expression matching fails before BPE. Our approach demonstrates higher and more stable throughput compared to baseline methods. Notably, tiktoken exhibits a characteristic decay as input length increases, reflecting its underlying O(n 2 ) complexity.

ment for Hugging Face's tokenizers and OpenAI's tiktoken. Since our algorithm is fully compatible with existing pipelines, the benchmarks isolate the effect of replacing the BPE stage alone, without altering segmentation, normalization, or caching behavior.

Detailed experimental setup, dataset composition, and execution strategies are provided in Appendix [H,](#page-21-1) while the full benchmark results (including eager output) are listed in Table [5.](#page-23-0)

### 7.1. Throughput Analysis

Table [1](#page-7-0) reports the speedup factors evaluated on concatenated documents from each dataset.

Absence of Pre-tokenization. The most substantial gains are observed in CodeLlama (up to 3.13×), where the BPE processes normalized text without regex-based pretokenization. In this regime, the heap-based implementation in tokenizers faces log-linear complexity over the full input length, whereas our algorithm leverages its incremental nature to maintain high throughput.

Coarse-Grained Segmentation. For the Chinese dataset, regex-based pre-tokenization typically yields coarser segments than English due to the specific designs of the regex rules and the characteristics of the language.

This exposes the performance bottlenecks in the original BPE implementation of tiktoken, while our method achieves significant speedups (up to 1.59×) by strictly bounding the per-byte processing time.

Fine-Grained Segmentation. For the English dataset, regex rules effectively partition the input into small chunks, where the constant factors of the implementation overhead

become dominant. This explains the slight regression of our method observed in some cases.

<span id="page-7-0"></span>*Table 1.* End-to-end throughput speedup. We report the speedup factor of our incremental BPE as a drop-in replacement for Hugging Face's tokenizers and OpenAI's tiktoken (using default configurations with short-string caches enabled where applicable). CodeLlama shows the highest gains due to the absence of regex-based pre-tokenization.

| Tokenizer    | Model English | Chinese | Code   |   |
|--------------|---------------|---------|--------|---|
| CodeLlama    | 3.13          | × 1.10  | × 2.88 | × |
| Qwen-3       | 1.05          | × 1.04  | × 1.08 | × |
| DeepSeek-3.2 | 1.01          | × 0.93  | × 1.03 | × |
| Ouro         | 1.00          | × 1.02  | × 1.02 | × |
| Llama-3.1 *  | 0.99          | × 1.03  | × 1.02 | × |
| GPT-OSS      | 1.00          | × 1.08  | × 1.01 | × |
| Llama-4      | 1.01          | × 1.01  | × 1.00 | × |
| Mistral-3    | 1.00          | × 1.04  | × 0.99 | × |
| P50K         | 0.97          | × 1.35  | × 1.07 | × |
| R50K         | 0.96          | × 1.35  | × 1.05 | × |
| CL100K       | 0.96          | × 1.59  | × 1.04 | × |
| O200K        | 0.99          | × 1.46  | × 1.00 | × |

\* Properized dictionary. See Appendix [A](#page-11-0) for discussion on compatibility and non-properizable cases (e.g., Gemma-3).

### 7.2. Robustness and Eager Output

Pathological Inputs. We test robustness using inputs constructed by repeating the character 'a' 2 k times. As shown in Figure [3](#page-7-1) and Figure [7,](#page-27-1) tiktoken exhibits a characteristic throughput decay consistent with O(<sup>n</sup> 2 ) complexity.

Our method maintains stable throughput throughout the tests. The other tested tokenizers within the same frameworks exhibit similar trend characteristics to the representative models shown. Notably, specifically for the O200K model as an exception, long inputs trigger errors in the regex stage before BPE.

Eager Output Overhead. We also evaluate our *eager output* implementation (Section [6\)](#page-6-0). Results in Appendix [H](#page-21-1) indicate that eager output introduces an overhead on the order of 10% in end-to-end throughput compared to the noneager incremental implementation. This overhead stems from the additional bookkeeping required to maintain output states, and can potentially be amortized in systems where tokenization is pipelined with I/O or model inference.

# 8. Future Work

While this work demonstrates that the BPE stage itself is fully compatible with streaming input and output, other components in existing pipelines, notably normalization and regex-based pre-tokenization, remain offline-oriented and impede end-to-end streaming execution.

Our profiling results in Appendix [I](#page-26-0) indicate that these upstream stages can become computational bottlenecks.

A critical direction for future work is therefore to revisit the design choices of pre-tokenization in light of incremental algorithms with explicit worst-case guarantees.

# 9. Conclusion

We introduced a novel algorithm for incremental BPE tokenization with a strict worst-case time complexity of O(<sup>n</sup> log<sup>2</sup> t). Implemented as a drop-in replacement, the algorithm delivers substantial end-to-end speedups over existing systems and avoids the severe performance degradation on pathological inputs. Beyond performance, our results show that BPE can be made compatible with streaming input and output, enabling optimizations in modern language model systems.

Overall, our approach proves that strict algorithmic worstcase guarantees can translate into practical benefits, paving the way for more robust and responsive LLM pipelines.

# Acknowledgements

This work was supported by the National Natural Science Foundation of China (Nos. 62525601, 62476018) and the Postdoctoral Fellowship Program of CPSF (No. BX20250487).

# <span id="page-8-3"></span>Impact Statement

This paper presents work whose goal is to advance the field of machine learning by improving the fundamental algorithmic infrastructure of large language models (LLMs).

Energy Efficiency. Tokenization is a ubiquitous preprocessing step executed trillions of times in modern LLM pipelines. By reducing the algorithmic worst-case time complexity of BPE to O(<sup>n</sup> log<sup>2</sup> t), utilizing incremental updates for streaming input, and enabling eager emission for streaming output, our approach reduces the computational resources and latency required for processing. This optimization contributes to the broader goal of "Green AI," potentially lowering the aggregate energy consumption and carbon footprint associated with deploying large-scale language models.

System Robustness and Reliability. Our work specifically addresses performance degradation on pathological inputs, a vulnerability present in some current state-of-theart tokenizers. By providing strict worst-case execution guarantees, our algorithm mitigates the risk of algorithmic complexity attacks (e.g., Denial-of-Service attacks triggered by carefully crafted input sequences), thereby enhancing the reliability and security of production systems.

We do not foresee any specific negative societal consequences directly stemming from this algorithmic improvement, beyond the general dual-use nature of efficient computing infrastructure.

# References

<span id="page-8-5"></span><span id="page-8-4"></span><span id="page-8-2"></span><span id="page-8-1"></span><span id="page-8-0"></span>Aho, A. V. and Corasick, M. J. Efficient string matching: An aid to bibliographic search. *Communications of the ACM*, 18(6):333–340, June 1975. doi: 10.1145/360825.360855. Berglund, M. and van der Merwe, B. Formalizing BPE tokenization. *Electronic Proceedings in Theoretical Computer Science*, 388:16–27, September 2023. doi: 10.4204/eptcs.388.4. ByteDance. Scaling latent reasoning via looped language models, October 2025a. URL [https://arxiv.or](https://arxiv.org/abs/2510.25741) [g/abs/2510.25741](https://arxiv.org/abs/2510.25741). ByteDance. Ouro tokenizer. Hugging Face model repository, October 2025b. URL [https://huggingface.co](https://huggingface.co/ByteDance/Ouro-2.6B) [/ByteDance/Ouro-2.6B](https://huggingface.co/ByteDance/Ouro-2.6B). Accessed: 2026-01-01. DeepSeek-AI. DeepSeek-V3.2: Pushing the frontier of open large language models, December 2025a. URL <https://arxiv.org/abs/2512.02556>. DeepSeek-AI. DeepSeek-V3.2 tokenizer. Hugging Face model repository, December 2025b. URL [https://](https://huggingface.co/deepseek-ai/DeepSeek-V3.2) [huggingface.co/deepseek-ai/DeepSeek-V](https://huggingface.co/deepseek-ai/DeepSeek-V3.2) [3.2](https://huggingface.co/deepseek-ai/DeepSeek-V3.2). Accessed: 2026-01-01.

<span id="page-9-22"></span><span id="page-9-21"></span><span id="page-9-20"></span><span id="page-9-19"></span><span id="page-9-18"></span><span id="page-9-17"></span><span id="page-9-16"></span><span id="page-9-15"></span><span id="page-9-14"></span><span id="page-9-13"></span><span id="page-9-12"></span><span id="page-9-11"></span><span id="page-9-10"></span><span id="page-9-9"></span><span id="page-9-8"></span><span id="page-9-7"></span><span id="page-9-6"></span><span id="page-9-5"></span><span id="page-9-4"></span><span id="page-9-3"></span><span id="page-9-2"></span><span id="page-9-1"></span><span id="page-9-0"></span>Devlin, J., Chang, M.-W., Lee, K., and Toutanova, K. BERT: Pre-training of deep bidirectional transformers for language understanding. In Burstein, J., Doran, C., and Solorio, T. (eds.), *Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers)*, pp. 4171–4186, Minneapolis, Minnesota, June 2019. Association for Computational Linguistics. doi: 10.18653/v1/N19-1423. Gage, P. A new algorithm for data compression. *The C Users Journal*, 12(2):23–38, February 1994. URL [https://](https://dl.acm.org/doi/10.5555/177910.177914) [dl.acm.org/doi/10.5555/177910.177914](https://dl.acm.org/doi/10.5555/177910.177914). GitHub. rust-gems: A collection of Rust algorithms and data structures. GitHub repository, 2026. URL [https:](https://github.com/github/rust-gems) [//github.com/github/rust-gems](https://github.com/github/rust-gems). Accessed: 2026-03-31. Gjengset, J. inferno: A Rust port of flamegraph. GitHub repository, 2026. URL [https://github.com/jon](https://github.com/jonhoo/inferno) [hoo/inferno](https://github.com/jonhoo/inferno). Accessed: 2026-01-01. Google. Gemma 3 technical report, March 2025a. URL <https://goo.gle/Gemma3Report>. Google. Gemma-3 tokenizer. Hugging Face model repository, March 2025b. URL [https://huggingface.](https://huggingface.co/google/gemma-3-27b-it) [co/google/gemma-3-27b-it](https://huggingface.co/google/gemma-3-27b-it). Accessed: 2026- 01-01. Hugging Face. Tokenizers: Fast state-of-the-art tokenizers optimized for research and production. GitHub repository, 2026. URL [https://github.com/huggingfa](https://github.com/huggingface/tokenizers) [ce/tokenizers](https://github.com/huggingface/tokenizers). Accessed: 2026-01-01. Kanda, S., Akabe, K., and Oda, Y. Engineering faster double-array Aho–Corasick automata. *Software: Practice and Experience*, 53(6):1332–1361, June 2023. doi: 10.1 002/spe.3190. Kudo, T. Subword regularization: Improving neural network translation models with multiple subword candidates. In Gurevych, I. and Miyao, Y. (eds.), *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pp. 66–75, Melbourne, Australia, July 2018. Association for Computational Linguistics. doi: 10.18653/v1/P18-1007. Kudo, T. and Richardson, J. SentencePiece: A simple and language independent subword tokenizer and detokenizer for neural text processing. In *Proceedings of the 2018 conference on empirical methods in natural language processing: System demonstrations*, pp. 66–71, August 2018. doi: 10.18653/v1/D18-2012. Leijen, D., Zorn, B., and de Moura, L. Mimalloc: Free list sharding in action. In Lin, A. W. (ed.), *Programming Languages and Systems*, pp. 244–265. Springer International Publishing, December 2019. doi: 10.1007/978-3-030-3 4175-6 13. Meta AI. Code Llama: Open foundation models for code, August 2023. URL [https://arxiv.org/abs/23](https://arxiv.org/abs/2308.12950) [08.12950](https://arxiv.org/abs/2308.12950). Meta AI. The Llama 3 herd of models, July 2024. URL <https://arxiv.org/abs/2407.21783>. Meta AI. The Llama 4 herd: The beginning of a new era of natively multimodal ai innovation, April 2025. URL [https://ai.meta.com/blog/llama-4-mul](https://ai.meta.com/blog/llama-4-multimodal-intelligence/) [timodal-intelligence/](https://ai.meta.com/blog/llama-4-multimodal-intelligence/). Meta Llama. Code Llama tokenizer. Hugging Face model repository, August 2023. URL [https://huggingf](https://huggingface.co/codellama/CodeLlama-13b-Instruct-hf) [ace.co/codellama/CodeLlama-13b-Instr](https://huggingface.co/codellama/CodeLlama-13b-Instruct-hf) [uct-hf](https://huggingface.co/codellama/CodeLlama-13b-Instruct-hf). Accessed: 2026-01-01. Meta Llama. Llama-3.1 tokenizer. ModelScope model repository, December 2024. URL [https://models](https://modelscope.cn/models/LLM-Research/Meta-Llama-3.1-8B) [cope.cn/models/LLM-Research/Meta-Lla](https://modelscope.cn/models/LLM-Research/Meta-Llama-3.1-8B) [ma-3.1-8B](https://modelscope.cn/models/LLM-Research/Meta-Llama-3.1-8B). Accessed: 2026-01-01. Meta Llama. Llama-4 tokenizer. ModelScope model repository, April 2025. URL [https://modelscope.c](https://modelscope.cn/models/LLM-Research/Llama-4-Maverick-17B-128E) [n/models/LLM-Research/Llama-4-Maveric](https://modelscope.cn/models/LLM-Research/Llama-4-Maverick-17B-128E) [k-17B-128E](https://modelscope.cn/models/LLM-Research/Llama-4-Maverick-17B-128E). Accessed: 2026-01-01. Mistral AI. Mistral Large 3: A state-of-the-art open model, December 2025a. URL [https://mistral.ai/n](https://mistral.ai/news/mistral-3/) [ews/mistral-3/](https://mistral.ai/news/mistral-3/). Mistral AI. Mistral-Large-3 tokenizer. Hugging Face model repository, December 2025b. URL [https://huggin](https://huggingface.co/mistralai/Mistral-Large-3-675B-Instruct-2512) [gface.co/mistralai/Mistral-Large-3-6](https://huggingface.co/mistralai/Mistral-Large-3-675B-Instruct-2512) [75B-Instruct-2512](https://huggingface.co/mistralai/Mistral-Large-3-675B-Instruct-2512). Accessed: 2026-01-01. OpenAI. gpt-oss-120b & gpt-oss-20b model card, August 2025a. URL [https://arxiv.org/abs/2508.1](https://arxiv.org/abs/2508.10925) [0925](https://arxiv.org/abs/2508.10925). OpenAI. gpt-oss-120b tokenizer. Hugging Face model repository, August 2025b. URL [https://huggin](https://huggingface.co/openai/gpt-oss-120b) [gface.co/openai/gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b). Accessed: 2026-01-01. OpenAI. OpenAI GPT-5 system card, January 2026a. URL <https://arxiv.org/abs/2601.03267>. OpenAI. tiktoken: A fast BPE tokenizer for use with OpenAI's models. GitHub repository, 2026b. URL <https://github.com/openai/tiktoken>. Accessed: 2026-01-01.

<span id="page-10-10"></span><span id="page-10-9"></span><span id="page-10-8"></span><span id="page-10-7"></span><span id="page-10-6"></span><span id="page-10-5"></span><span id="page-10-4"></span><span id="page-10-3"></span><span id="page-10-2"></span><span id="page-10-1"></span><span id="page-10-0"></span>Purplecoin. mimalloc rust: A Rust wrapper over microsoft's mimalloc memory allocator. GitHub repository, 2026. URL [https://github.com/purpleprotocol/](https://github.com/purpleprotocol/mimalloc_rust) [mimalloc_rust](https://github.com/purpleprotocol/mimalloc_rust). Accessed: 2026-01-01. Qwen Team. Qwen3 technical report, May 2025a. URL <https://arxiv.org/abs/2505.09388>. Qwen Team. Qwen3 tokenizer. Hugging Face model repository, September 2025b. URL [https://huggingfac](https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Thinking) [e.co/Qwen/Qwen3-Next-80B-A3B-Thinking](https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Thinking). Accessed: 2026-01-01. Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., Zhou, Y., Li, W., and Liu, P. J. Exploring the limits of transfer learning with a unified text-to-text transformer. *J. Mach. Learn. Res.*, 21(1), January 2020. URL [http://jmlr.org/papers/v21/20-074](http://jmlr.org/papers/v21/20-074.html) [.html](http://jmlr.org/papers/v21/20-074.html). Schuster, M. and Nakajima, K. Japanese and korean voice search. In *2012 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)*, pp. 5149– 5152, March 2012. doi: 10.1109/ICASSP.2012.6289079. Sennrich, R., Haddow, B., and Birch, A. Neural machine translation of rare words with subword units. In Erk, K. and Smith, N. A. (eds.), *Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pp. 1715–1725, Berlin, Germany, August 2016. Association for Computational Linguistics. doi: 10.18653/v1/P16-1162. Together Computer. RedPajama: An open source recipe to reproduce LLaMA training dataset. GitHub repository, April 2023a. URL [https://github.com/tog](https://github.com/togethercomputer/RedPajama-Data) [ethercomputer/RedPajama-Data](https://github.com/togethercomputer/RedPajama-Data). Accessed: 2026-01-01. Together Computer. RedPajama-Data-1T dataset. Hugging Face dataset repository, April 2023b. URL [https:](https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T) [//huggingface.co/datasets/togetherco](https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T) [mputer/RedPajama-Data-1T](https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T). Accessed: 2026- 01-01. van Antwerpen, H. and Neubeck, A. So many tokens, so little time: Introducing a faster, more flexible byte-pair tokenizer. The GitHub Blog, December 2024. URL [https://github.blog/ai-and-ml/llms/s](https://github.blog/ai-and-ml/llms/so-many-tokens-so-little-time-introducing-a-faster-more-flexible-byte-pair-tokenizer/) [o-many-tokens-so-little-time-introdu](https://github.blog/ai-and-ml/llms/so-many-tokens-so-little-time-introducing-a-faster-more-flexible-byte-pair-tokenizer/) [cing-a-faster-more-flexible-byte-pai](https://github.blog/ai-and-ml/llms/so-many-tokens-so-little-time-introducing-a-faster-more-flexible-byte-pair-tokenizer/) [r-tokenizer/](https://github.blog/ai-and-ml/llms/so-many-tokens-so-little-time-introducing-a-faster-more-flexible-byte-pair-tokenizer/). Wikimedia Foundation. Wikimedia downloads, November 2023a. URL <https://dumps.wikimedia.org>. Wikimedia Foundation. Wikipedia dataset. Hugging Face dataset repository, November 2023b. URL [https://](https://huggingface.co/datasets/wikimedia/wikipedia) [huggingface.co/datasets/wikimedia/wi](https://huggingface.co/datasets/wikimedia/wikipedia) [kipedia](https://huggingface.co/datasets/wikimedia/wikipedia). Accessed: 2026-01-01.

## <span id="page-11-0"></span>A. Properizing

### A.1. Semantics Discrepancy

As discussed by [Berglund & van der Merwe](#page-8-0) [\(2023\)](#page-8-0), Byte Pair Encoding (BPE) tokenization generally follows one of two distinct operational semantics:

- 1. Standard BPE Semantics (as defined in Section [3.1\)](#page-2-1): This approach operates on a *fixed priority schedule*. It iterates through the merge rules from highest to lowest priority, applying each rule exhaustively across the sequence. Crucially, the process is linear with respect to the rule list: once a priority level is passed, the algorithm never revisits it, regardless of whether subsequent merges create new opportunities for higher-priority rules.
- 2. SentencePiece Semantics [\(Kudo & Richardson,](#page-9-7) [2018\)](#page-9-7): This approach operates on a *dynamic priority queue*. At each step, it identifies the adjacent token pair with the global maximum priority in the current sequence. Notably, a merge operation generates at most two new adjacent pairs that may possess even higher priorities. SentencePiece will immediately execute either of the merges, effectively "growing" the token recursively and prioritizing these local expansions over the previous lower-priority global candidates.

To formalize this inconsistency, we adopt the terminology established by [Berglund & van der Merwe](#page-8-0) [\(2023\)](#page-8-0). An *improper dictionary* is defined as one containing merge rules that violate the sequential assumption of the standard BPE. Specifically, if a rule r<sup>l</sup> produces a token that creates the context for a strictly higher-priority rule rh, the standard BPE will not execute rh, since the algorithm has strictly proceeded past its priority level. In contrast, SentencePiece would immediately identify r<sup>h</sup> as the new global maximum.

To bridge this inconsistency, we propose a method to properize the dictionary: reassigning rule priorities via topological sorting so that the standard BPE's execution yields results identical to those of SentencePiece. The method is a sufficient construction for properization by reordering the priorities; other constructions may exist to achieve the same goal.

### A.2. Dictionary Filtering

In practice, BPE dictionaries often contain redundant or unreachable rules that are never triggered, even under SentencePiece semantics. To ensure the formalization is well-defined, we restrict our analysis to valid rules prior to properization.

Given the deterministic nature of BPE, we define a merge rule (x, y) → <sup>z</sup> as *valid* if and only if the tokenization of the concatenated string xy under SentencePiece semantics results in the single token z itself, and the final applied merge is indeed (x, y). Rules failing this condition are effectively unreachable in any context and are thus discarded.

Crucially, this implies that the mapping from a produced token to its generating rule is unique; no two distinct valid rules result in the same token after filtering.

In the remainder of this section, we assume the dictionary has been filtered to contain solely valid rules. Based on this filtered dictionary, we can now define the dependency structure.

## A.3. Growing Tree

The SentencePiece semantics can be conceptualized as the standard BPE mechanism equipped with additional growing steps. Under this view, a merge operation (x0, y0) → <sup>z</sup><sup>0</sup> serves as a *seed event* that may trigger a cascade of immediate high-priority merges due to the greedy strategy.

Specifically, after the seed merge (x0, y0), the new token z<sup>0</sup> immediately forms new pairs with its left neighbor (u1, z0) and right neighbor (z0, v1). If either of these new pairs has a strictly higher priority than the original seed (x0, y0), SentencePiece will immediately execute the one with the higher priority. Note that executing one side implicitly invalidates the other, as the central token z<sup>0</sup> is consumed.

This recursive process, denoted as (xk, yk) → <sup>z</sup>k, repeats until no adjacent pair has a higher priority than the original seed (x0, y0). The entire sequence behaves like "growing" outward from the initial seed merge. Note that, since the length of the merged token z<sup>k</sup> strictly increases with each step, no subsequent adjacent pair will possess the exact same priority as the seed.

forming a chain of growing steps. We formalize the collection of all such possible growing steps as the Growing Tree. Specifically, the root is the seed rule, and the child nodes are all valid merge rules that can be triggered by the parent during the growing of the root, distinguished by their growing direction (left or right).

To systematically construct these trees, we analyze the derivation of each valid rule to determine its role (root or child). For any string s, let L(s) denote the lowest priority among all merge rules involved in the tokenization of s under SentencePiece semantics. For a valid merge rule <sup>r</sup> : (x, y) → <sup>z</sup>, it inherently holds that <sup>L</sup>(z) ≤ min(L(x), L(y)). We classify the rule <sup>r</sup> based on this relationship:

- 1. Root Rule (L(z) < min(L(x), L(y))): The rule r has a lower priority than any rule contained within its components. Thus, r is a seed event that initiates a growing process. In the Growing Tree, r is a root node. Functionally, we treat the root as *left-growing*, since the rule becomes applicable only after the token y is generated.
- 2. Growing Step (L(z) = min(L(x), L(y))): The rule r is triggered by a lower-priority bottleneck within its components. We determine the growing direction as follows:
  - Left-Growing: If L(z) = L(y), the seed lies within y. Rule r extends the growing chain to the left. Crucially, this case covers the scenario where L(x) = L(y). Under SentencePiece semantics, such ties must be resolved as left-growing; otherwise, the necessary right-side token y would not yet be established to participate in the merge. In the tree, r is a child of the corresponding rule in y.
  - Right-Growing: If L(z) = L(x) and L(z) < L(y), the seed lies within x. Rule r extends the growing chain to the right. In the tree, r is a child of the corresponding rule in x.

Since the dictionary is filtered to ensure unique derivations, each merge rule corresponds to at most one parent, ensuring the dependency structure forms a valid forest.

Consequently, the growing process of a seed merge under SentencePiece semantics is equivalent to a greedy search for the deepest applicable path within the Growing Tree rooted at that seed.

## A.4. Dependency Graph and Topological Sort

To simulate SentencePiece semantics using the standard BPE, we need to flatten each Growing Tree into a valid sequential order, by reordering the priorities of rules during growing steps.

However, the growing steps are applied independently for each seed under SentencePiece semantics, while using the standard BPE requires each rule to be applied to the sequence exhaustively. We model the relative order and independence of growing steps as a dependency graph.

- 1. Tree Edges (Parent → Child): Within each Growing Tree, a parent rule must be processed before its children. Although the children originally had higher priorities, in the properized dictionary, we must place them *after* the parent to ensure the parent exists to trigger them.
- 2. Sibling Edges (Among the Direct Children): For siblings, during the growing steps, only the highest-prioritized applicable merge is selected. This implies that sibling rules are evaluated strictly in the order of their original priorities. Thus, we add edges from the siblings with higher priority to those with lower priority.
- 3. Conflict Edges (Right-Growing → Left-Growing): A critical inconsistency arises when two growing steps from different trees compete for the same overlapping token. Suppose a *left-growing* rule (w, x) and a *right-growing* rule (y, w) both require token w.
  - Under SentencePiece semantics, each growing process runs independently, so the leftmost seed can obtain w before others.
  - To emulate this deterministically without lookahead, we rely on the left-to-right scan nature of the standard BPE.
  - This imposes the constraint that right-growing nodes must precede left-growing nodes.

One can optimize the number of edges via transitive reduction. This simplifies the graph without altering its topological properties.

If the constructed dependency graph is a directed acyclic graph (DAG), a topological sort exists. Deriving the new rule priorities from this topological order yields a properized dictionary. The standard BPE, executing this dictionary linearly, will respect all dependencies of the growing steps and produce output identical to SentencePiece.

### A.5. Sufficiency

Theorem A.1 (Sufficiency). *For any acyclic dependency graph, the derived properized dictionary yields tokenization results under the standard BPE that are identical to those under SentencePiece semantics.*

*Proof.* The proof establishes that a topological order exists to reconcile the execution discrepancy between the standard BPE and SentencePiece semantics.

- Execution Discrepancy: The standard BPE applies each merge rule globally and exhaustively across the entire sequence. In contrast, SentencePiece processes seeds sequentially from left to right, completing all recursive growing steps for the current seed before considering the next.
- Intra-tree Consistency: In the absence of conflicts between seeds with the same priority, the *Tree Edges* and *Sibling Edges* are sufficient to simulate SentencePiece's behavior. These edges ensure that the traversal of the deepest applicable path within each growing tree is executed in the correct dependency order.
- Inter-tree Conflict Resolution: When growing steps from different seeds of the same priority compete for overlapping tokens, SentencePiece inherently prioritizes the leftmost seed. To simulate this without lookahead, the *Conflict Edges* ensure that right-growing steps precede left-growing steps, effectively granting priority to the leftmost seeds within the global scan.

If the resulting dependency graph is a DAG, the topological sort provides a static priority order that ensures the standard BPE's global execution results in identical outputs.

Since *Tree Edges* and *Sibling Edges* define a directed forest, they are inherently acyclic. A cycle would only indicate a conflict between growing processes that cannot be resolved via static priority reordering.

## <span id="page-13-1"></span>A.6. Non-properizable scenarios

If the graph contains a cycle, the dictionary is non-properizable.

A canonical example is the dictionary [(aa, a), (a, a)] applied to the string "aaaa".

- SentencePiece: yields [aaa, a].
- The standard BPE: yields [aa, aa], no matter the priorities of the merge rules.

In the dependency graph, (a, a) acts as a root (left-growing) pointing to a right-growing node (aa, a). However, the *Conflict Edges* would cause a dependency cycle, so it fails to properize.

In our experiments, one non-properizable tokenizer we found is Gemma-3 [\(Google,](#page-9-8) [2025b\)](#page-9-8), which contains improper merge rules of multiple newline characters.

# <span id="page-13-0"></span>B. Proof of the Prefix Consistency

In this section, we provide the formal proof for Lemma [3.1.](#page-2-0) Our proof relies on the inductive properties of the single merge operation visualized in Figure [4.](#page-14-0)

Notation. Let T(u,v) denote the operator for a single BPE merge step that replaces all adjacent occurrences of tokens (u, v) from left to right with the merged token w. Initially, the input string s is mapped to a sequence of atomic tokens φ0. The full BPE process is a composition of such operators: T <sup>=</sup> T<sup>r</sup><sup>m</sup> ◦ · · · ◦ T<sup>r</sup><sup>1</sup> , where r1, . . . , r<sup>m</sup> are the merge rules applied in order.

*Proof.* We prove the lemma by induction on the number of merge steps.

Base Case (0 merges): The initial token sequence φ<sup>0</sup> consists of atomic tokens (bytes/characters). The boundaries are fixed at every character position. Trivially, any prefix of the atomic token sequence corresponds to the prefix of the raw text.

Inductive Step: Assume the consistency property holds for the state φ<sup>k</sup> after k merges. Consider the (k + 1)-th merge rule <sup>r</sup> = (u, v) → <sup>w</sup>. Let the state transition be <sup>φ</sup>k+1 <sup>=</sup> Tr(φk). Let <sup>µ</sup> be any prefix of the new token sequence <sup>φ</sup>k+1.

We examine the boundary at the end of µ. Since T<sup>r</sup> is a boundary elimination operation, it only removes the internal boundaries between instances of u and v sequentially from left to right. It does not shift or create boundaries. Therefore, the boundary ending µ must have existed in the previous state φk. This implies there exists a unique prefix η in φ<sup>k</sup> such that π(η) = π(µ).

Since Tr(η) = µ (as the merge operation is local and respects the boundary), and η is a valid tokenization by hypothesis, it follows that µ is the valid tokenization of π(µ) after the (k + 1)-th step.

<span id="page-14-0"></span>
$$\mathbb{T}_{(u,v)}(\varphi) = \underbrace{\diamond w_1 \diamond \cdots \diamond u \quad v \diamond \cdots \diamond w_k \diamond w_{k+1} \diamond \cdots \diamond u \quad v \diamond \cdots \diamond w_n \diamond \cdots \diamond w_m \diamond}_{\eta: \pi(\eta) = \pi(\mu)}$$

*Figure 4.* Inductive step of the Prefix Consistency. Solid/dashed arrows mark surviving/eliminated boundaries during a merge (u, v). For any prefix µ in the post-merge token sequence, there exists exactly one valid prefix η in the pre-merge token sequence with π(η) = π(µ). Notably, applying the single merge step to <sup>η</sup> yields exactly <sup>µ</sup> <sup>=</sup> T(u,v)(η). This proves the lemma by induction over the full tokenization process.

# <span id="page-14-1"></span>C. Normalization and Equivalence Details

In this section, we elaborate on the properties of the normalized representation introduced in Section [3.3.](#page-3-1)

Canonical Generation and Closure. For a canonical token <sup>t</sup> produced eventually by the rule (x, y) → <sup>t</sup>, the tokenization of the string t must conclude with this specific merge. This necessitates that the substrings x and y must have been independently tokenized into x and y prior to this final merge. Therefore, T(x) = [x] and T(y) = [y], implying that the predecessor pre(t) = <sup>x</sup> and successor suc(t) = <sup>y</sup> are themselves canonical tokens. This ensures that V is closed under decomposition, which is essential for the construction of the Successor Forest.

Equivalence. Normalization does not alter tokenization results for general text. Since non-canonical rules are by definition never triggered in the deterministic BPE tokenization of valid tokens, removing them from the dictionary does not affect the merge process for any input string. Thus, TD(s) ≡ TD(s).

# <span id="page-14-2"></span>D. Extended Intuition of Monotonic Path: Boundary Elimination

In this section, we expand on the intuition provided in Section [4.1](#page-3-2) by reasoning about the merge process of the rightmost token.

Fix a non-empty string s and a suffix token t of s. Let s <sup>−</sup> suc(t) denote the shorter prefix obtained by removing the suffix suc(t) from s. If t is ever produced as the last token during the merge process, then immediately before applying the canonical rule of t, the tokens pre(t) and suc(t) must appear consecutively at the end of the current token sequence.

Crucially, at this specific moment, the boundary between pre(t) and suc(t) remains intact, so the presence of the rightmost token suc(t) does not affect any merges that have already occurred to the left of pre(t). Therefore, the token sequence obtained by removing the final suc(t) coincides with the token sequence produced by the merge process of s − suc(t) right before applying the rule of t.

This implies a necessary condition: if t is to be formed, pre(t) must appear as the rightmost token at some stage during the merge process of s − suc(t) . In terms of the Successor Forest structure, this means that the eventual last token θ(s − suc(t) ) must be a descendant of pre(t) (or pre(t) itself).

Additionally, whether this state is reachable depends on rule priorities. If pre(t) is not yet the final result θ(s − suc(t) ), it is destined to be merged with a left neighbor to form a larger token (specifically, one of its children in the Successor Forest, formed by merging it with its left neighbor). For t to exist, the canonical rule of t must be applied *before* this specific merge event occurs.

In summary, the formation of t is determined by a single critical moment: whether pre(t) can persist as the rightmost token of s <sup>−</sup> suc(t) until the canonical rule of t is applied.

# <span id="page-15-0"></span>E. Proof of Monotonic Path Property

In this section, we prove Theorem [4.2,](#page-4-1) which characterizes the structure of suffix tokens that satisfy the Prefix Last-Token Condition (Definition [4.1\)](#page-3-0).

Recall that for a non-empty string s, let k be the longest canonical suffix token of s, and let SufSucTree(k) denote the Suffix-Successor Tree induced by all canonical suffix tokens of k. The theorem asserts that the set of tokens in SufSucTree(k) satisfying the Prefix Last-Token Condition forms exactly the unique path from the true last token θ(s) to the root of SufSucTree(k).

## E.1. Proof Overview

As discussed in Section [4.1](#page-3-2) and Appendix [D,](#page-14-2) the Prefix Last-Token Condition (Definition [4.1\)](#page-3-0) can be intuitively understood as the ability of a node w to *"steal"* its predecessor pre(w) from the last token θ(s − suc(w) ) of the truncated string.

Claim 1 establishes an *upward-closure* property: if a node has this stealing capability, then its successor must also have it. Otherwise, the canonicity of the involved tokens would be violated.

Claim 2 addresses the question of uniqueness: whether multiple children of the same successor could simultaneously satisfy the condition. The determinism of the standard BPE merge process, together with strict priority ordering, rules out this possibility.

Claim 3 confirms that the true last token θ(s) indeed satisfies the condition. Intuitively, since θ(s) is produced by the final merge, it necessarily has the ability to steal pre(θ(s)).

Finally, Claim 4 shows that the answer node θ(s) cannot be further extended: if it could steal once more, it would not be the last token of the final tokenization of the string.

With these claims, the Monotonic Path Property follows.

## E.2. Detailed Proof

We begin by introducing auxiliary notation and several structural lemmas that will be used throughout the proof.

Ancestor Path. For any canonical token <sup>x</sup> ∈ V, we define <sup>P</sup>(x) to be the unique path from <sup>x</sup> to the root of the Successor Forest Fsuc, following successor edges. Equivalently, <sup>P</sup>(x) consists of <sup>x</sup> and all of its ancestors in the Successor Forest.

Since the Successor Forest is acyclic and every non-atomic token has a unique successor, P(x) is well-defined and totally ordered by ancestry.

Rule Priority Convention. Throughout the proof, we compare merge rules by their execution order in the dictionary: a rule r<sup>i</sup> has higher priority than r<sup>j</sup> (i.e., r<sup>i</sup> > r<sup>j</sup> ) if and only if r<sup>i</sup> is applied earlier in the standard BPE merge process.

Lemma E.1 (Priority Monotonicity Along Successor Paths). *Let* x, y ∈ V *be canonical tokens such that* <sup>y</sup> *is a descendant of* <sup>x</sup> *in the Successor Forest (i.e.,* <sup>x</sup> ∈ <sup>P</sup>(y)*). If the token* <sup>x</sup> *is non-atomic, then the canonical merge rule producing the token* x *has strictly higher priority than the canonical merge rule producing the token* y*.*

*Proof.* By definition of the Successor Forest, y is obtained by a sequence of canonical merges starting from x. If the canonical rule producing y were applied before the canonical rule producing x, then x would never appear as an isolated token during the tokenization of its own string, contradicting the assumption that x is canonical.

Lemma E.2 (Shared Right Boundary). *Let* x, y ∈ V *be canonical tokens such that* <sup>x</sup> ∈ <sup>P</sup>(y)*. Consider any tokenization process in which the token* y *appears as a token in the token sequence. Immediately before the canonical rule producing the token* y *is applied, the token* x *must also appear as a token, and the right boundary of* x *coincides with the right boundary of* y*.*

*Proof.* Since y is produced by successive canonical merges starting from x, all intermediate merges preserve the rightmost boundary until the final merge forming y. Thus, prior to the execution of the canonical rule of y, the token x must exist and share the same right endpoint.

<span id="page-16-0"></span>Lemma E.3 (Ancestor Characterization of Last Tokens). *For any non-empty string* s *and any canonical token* x*, we have*

$$x \in P(\theta(s)) \iff x \text{ appears as the last token at some stage during the tokenization of the string } s.$$

*Proof.* (⇒) If <sup>x</sup> ∈ <sup>P</sup>(θ(s)), then <sup>θ</sup>(s) is obtained from <sup>x</sup> by a sequence of canonical merges. Immediately before each such merge, x (or its descendant) appears as the last token.

(⇐) If <sup>x</sup> appears as the last token at some stage, then the last token <sup>θ</sup>(s) must be obtained by further merges starting from <sup>x</sup>, implying <sup>x</sup> ∈ <sup>P</sup>(θ(s)).

<span id="page-16-2"></span>Lemma E.4 (Tokenization Consistency of Token-wise Truncation). *The Prefix Consistency (Lemma [3.1\)](#page-2-0) extends naturally to any contiguous subsequence of the token sequence during the tokenization. It also applies to any prefix of merge rules in a proper dictionary.*

*Specifically, for any integer* <sup>k</sup> ≤ |D|*, after applying the first* <sup>k</sup> *merge rules to a string and obtaining the token sequence* φ*, if we perform token-wise truncation on* φ*, the isolated contiguous subsequence* µ *is exactly the valid tokenization of its corresponding underlying string* π(µ) *with the first* k *merge rules.*

*Proof.* This follows directly from the inductive proof of Lemma [3.1,](#page-2-0) which applies to each individual merge step.

From a more abstract perspective, because the boundaries delimiting µ survive the first k merges, no merge operation has crossed them. Due to the deterministic, left-to-right, non-overlapping nature of BPE tokenization, the sequence of internal merges strictly within µ is entirely independent of the tokens outside these boundaries. Therefore, isolating µ via token-wise truncation yields the exact same state as independently tokenizing the raw string π(µ) with the first k rules.

<span id="page-16-3"></span>Lemma E.5 (Step-wise Consistency of Token-wise Truncation). *Let* s *be a string and* φ *be its token sequence after applying the first* k *merge rules. Let* µ *be a contiguous subsequence of* φ *obtained by token-wise truncation. Let* r *be the* (k + 1)*-th merge rule. Applying* r *to* µ *(i.e.,* Tr(µ)*) yields exactly the valid tokenization of the corresponding substring* π(µ) *with the first* k + 1 *merge rules.*

*Proof.* By Lemma [E.4,](#page-16-2) token-wise truncation is valid after k merges. Thus, µ is exactly the correct token sequence for the substring π(µ) after the first k rules.

By the definition of the BPE tokenization, the tokenization after k + 1 rules is obtained by applying the (k + 1)-th rule r directly to the tokenization resulting from the first k rules.

Therefore, Tr(µ) yields the tokenization of π(µ) after applying the first k + 1 merge rules.

<span id="page-16-1"></span>Lemma E.6 (Exclusive Priorities of Tokens satisfying the Prefix Last-Token Condition). *Let* t *be a non-atomic suffix token of a string* s *that satisfies the Prefix Last-Token Condition (Definition [4.1\)](#page-3-0). During the tokenization process of* s*, immediately prior to executing the canonical rule of* t*, the rightmost two tokens in the sequence are exactly* pre(t) *and* suc(t)*.*

*Proof.* For the string <sup>s</sup>, let the token boundary immediately to the left of the suffix string suc(t) be ♢suc(t) , the token boundary immediately to the left of the suffix string <sup>t</sup> be ♢t. We term the token boundaries strictly between ♢<sup>t</sup> and ♢suc(t) as the *internal boundaries* of pre(t).

The following proof will focus on the status of ♢t, ♢suc(t) , and the internal boundaries of pre(t).

Step 1: The internal boundaries of pre(t) must be eliminated first. We first prove that during the merges before applying the canonical rule of <sup>t</sup>, no rule can eliminate ♢<sup>t</sup> or ♢suc(t) before all token boundaries between them are eliminated.

Suppose a merge rule r attempts to eliminate one or more of these boundaries while at least one internal boundary still exists:

- If the rule <sup>r</sup> eliminates ♢t: By Lemma [E.5,](#page-16-3) we can perform token-wise truncation at ♢suc(t) immediately before the rule r, leaving the tokenization of the prefix string s − suc(t) . The tokenization before and after the rule r must be valid for s − suc(t) . However, with the merge rule <sup>r</sup>, ♢<sup>t</sup> is eliminated before the internal boundaries of pre(t) are cleared, pre(t) can never become an isolated token as the last token during the tokenization. This leads to pre(t) ∈/ <sup>P</sup>(θ(<sup>s</sup> − suc(t) )), which contradicts the Reachability condition.
- If the rule <sup>r</sup> eliminates ♢suc(t) while ♢<sup>t</sup> survives: We truncate at ♢t. The suffix should form the valid tokenization of <sup>t</sup>. However, the boundary between pre(t) and suc(t) is eliminated before the internal boundaries of pre(t) are cleared. This contradicts the proper merge sequence of the canonical token t.

Furthermore, if the internal boundaries exist, there are at least 3 consecutive token boundaries. Since BPE only merges adjacent pairs without overlapping, the rule r can eliminate at most half of the consecutive boundaries. Thus, it is impossible for all of ♢t, ♢suc(t) , and the internal boundaries of pre(t) to be eliminated simultaneously.

This confirms that any attempt to eliminate ♢<sup>t</sup> or ♢suc(t) must happen strictly after the internal boundaries are fully eliminated.

Furthermore, since the truncation between ♢<sup>t</sup> and ♢suc(t) yields the valid tokenization of pre(t), and the canonical rule of pre(t) has a strictly higher priority than the canonical rule of t (or pre(t) is an atomic token), it follows that immediately before executing the canonical rule of <sup>t</sup> during the tokenization of <sup>s</sup>, both ♢<sup>t</sup> and ♢suc(t) must survive without any internal boundaries between them, which means pre(t) between ♢<sup>t</sup> and ♢suc(t) should become a single isolated token.

Step 2: pre(t) cannot be consumed before the canonical rule of t is executed. Next, consider the process after pre(t) is completely formed but before the canonical rule of t is executed.

- If pre(t) merges leftward (acting as a successor): The boundary ♢<sup>t</sup> is eliminated. Since a single BPE merge eliminates at most one boundary around each token, ♢suc(t) must survive. Truncating at ♢suc(t) , the prefix corresponds to the tokenization of s − suc(t) . This merge implies pre(t) is merged into a larger token during the tokenization of s − suc(t) , so θ(s − suc(t) ) ̸= pre(t). By definition, the executed rule is exactly the unique child of pre(t) on <sup>P</sup>(θ(<sup>s</sup> − suc(t) )). However, the Priority dominance requires the canonical rule of t to have a strictly higher priority than this child. Thus, it is impossible for this merge to occur before the canonical rule of t, contradicting the assumption.
- If pre(t) merges rightward: The merge eliminates ♢suc(t) while ♢<sup>t</sup> survives. Truncating at ♢t, the suffix must represent the valid tokenization of t. However, the canonical rule of t is not yet applied, while the prefix token pre(t) merges rightward with a token other than suc(t). This contradicts the proper merge sequence of the canonical token t.

Step 3: The right side must solely be suc(t). Finally, immediately prior to executing the canonical rule of t, suppose there are still other surviving token boundaries between ♢suc(t) and the end of the sequence. If we truncate at ♢t, the isolated suffix sequence would contain more than two tokens. However, in the valid tokenization of the canonical token t, the token sequence exactly prior to applying its canonical rule must consist of exactly two tokens: pre(t) and suc(t). Contradiction.

With the above notation and lemmas in place, we now prove Theorem [4.2](#page-4-1) by establishing four structural claims: upward closure, uniqueness, validity of θ(s), and maximality.

Claim 1 (Upward Closure). Let s be a non-empty string and let k be the longest canonical suffix token of s. For any node <sup>w</sup> ∈ SufSucTree(k), if <sup>w</sup> satisfies the Prefix Last-Token Condition (Definition [4.1\)](#page-3-0) with respect to <sup>s</sup>, then its parent suc(w) in the Successor Forest (if it exists) also satisfies the Prefix Last-Token Condition.

*Proof.* If w is an atomic token, it is a root, making the claim vacuous. Assume w is non-atomic. Let v = suc(w). We aim to prove v satisfies the condition. If v is an atomic token, it satisfies the condition by definition. Thus, we further assume v is non-atomic.

Notations. We define the following components and their corresponding canonical merge rules:

- <sup>u</sup> = pre(w) and <sup>v</sup> = suc(w), with <sup>r</sup><sup>w</sup> being the canonical rule (u, v) → <sup>w</sup>.
- <sup>x</sup> = pre(v) and <sup>y</sup> = suc(v), with <sup>r</sup><sup>v</sup> being the canonical rule (x, y) → <sup>v</sup>.

Since w is a suffix of s and v is a suffix of w, the token y is exactly the suffix token of s. Let s <sup>−</sup><sup>y</sup> denote the prefix string obtained by removing y from s.

Step 1: Reachability. Because w satisfies the condition, Lemma [E.6](#page-16-1) guarantees that during the tokenization of s, immediately prior to executing rw, the rightmost two tokens are exactly u and v. The existence of the fully formed token v requires that its canonical rule r<sup>v</sup> must have been executed at some earlier stage.

Backtracking to the state immediately prior to the execution of rv, the token sequence must end exactly with x and y. At this specific moment, the token boundary between x and y exists. By Lemma [E.5,](#page-16-3) performing token-wise truncation at this boundary (removing y) yields the valid tokenization of s −y at this stage, ending with the token x. By Lemma [E.3,](#page-16-0) since x appears as the last token during the tokenization of s −y , we have <sup>x</sup> ∈ <sup>P</sup>(θ(<sup>s</sup> −y )). This establishes the Reachability condition for v.

Step 2: Priority Dominance. Suppose <sup>x</sup> ̸<sup>=</sup> <sup>θ</sup>(<sup>s</sup> −y ). This implies the final x of s <sup>−</sup><sup>y</sup> will eventually be consumed leftward by some merge rule r<sup>c</sup><sup>x</sup> to form c<sup>x</sup> (the unique child of x on P(θ(s −y ))).

Let φ be the token sequence of s immediately prior to executing rv. As established in Step 1, φ ends exactly with x and <sup>y</sup>, so we can write <sup>φ</sup> <sup>=</sup> <sup>η</sup> ⊕ [x, y] for some prefix sequence <sup>η</sup>. By Lemma [E.5,](#page-16-3) performing token-wise truncation yields <sup>µ</sup> <sup>=</sup> <sup>η</sup> ⊕ [x], which is exactly the token sequence of <sup>s</sup> −y at this same stage.

Since the final token x remains unmerged in µ, the rule r<sup>c</sup><sup>x</sup> has not yet been applied. Thus, r<sup>c</sup><sup>x</sup> cannot have a higher priority than rv.

Suppose their priorities are equal, meaning r<sup>c</sup><sup>x</sup> is exactly rv, i.e., c<sup>x</sup> = v. For r<sup>v</sup> to consume x leftward, given its definition (x, y) → <sup>v</sup>, we must have <sup>x</sup> <sup>=</sup> <sup>y</sup>. This makes the rule <sup>r</sup><sup>v</sup> = (x, x) → <sup>v</sup>. As <sup>r</sup><sup>c</sup><sup>x</sup> must be applied and alter the last token of T<sup>r</sup>cx (µ) to v, the token sequences can be written as µ = η ′ ⊕ [x, x] and <sup>φ</sup> <sup>=</sup> <sup>η</sup> ′ ⊕ [x, x, x]. Now consider the deterministic left-to-right matching of the rule (x, x) → <sup>v</sup>. Either T<sup>r</sup><sup>v</sup> (µ) or T<sup>r</sup><sup>v</sup> (φ) exactly ends with the token v, while the other ends with the token x, contradicting the analysis where both must end with v.

Therefore, the canonical rule r<sup>v</sup> must have a strictly higher priority than r<sup>c</sup><sup>x</sup> , satisfying the Priority dominance condition for token v with respect to s.

Conclusion. With both conditions verified, suc(w) = v satisfies the Prefix Last-Token Condition with respect to s.

Claim 2 (Uniqueness of the satisfying child). Let s be a non-empty string. For any node v, there exists *at most one* child w of v that satisfies the Prefix Last-Token Condition (Definition [4.1\)](#page-3-0) with respect to s.

*Proof.* Assume for contradiction that there exist two distinct nodes <sup>w</sup><sup>a</sup> ̸<sup>=</sup> <sup>w</sup><sup>b</sup> that both satisfy the condition with respect to s, and share the same successor v = suc(wa) = suc(wb). Let u<sup>a</sup> = pre(wa) and u<sup>b</sup> = pre(wb). Let r<sup>w</sup><sup>a</sup> = (ua, v) and <sup>r</sup><sup>w</sup><sup>b</sup> = (ub, v). Since <sup>w</sup><sup>a</sup> ̸<sup>=</sup> <sup>w</sup>b, we have <sup>u</sup><sup>a</sup> ̸<sup>=</sup> <sup>u</sup>b.

By the Reachability condition, both <sup>u</sup>a, u<sup>b</sup> ∈ <sup>P</sup>(θ(<sup>s</sup> −v )). Since P(θ(s −v )) is a chain on a tree, one must be an ancestor of the other. Without loss of generality, assume <sup>u</sup><sup>a</sup> is a proper ancestor of <sup>u</sup>b. Thus <sup>u</sup><sup>a</sup> ̸<sup>=</sup> <sup>θ</sup>(<sup>s</sup> −v ).

This implies that during the tokenization of s −v , the token u<sup>a</sup> is formed earlier than u<sup>b</sup> and is required to form ub. For u<sup>b</sup> to eventually form, <sup>u</sup><sup>a</sup> must uniquely merge leftward via some rule <sup>r</sup>c<sup>a</sup> = (k, ua) → <sup>c</sup>a, where <sup>c</sup><sup>a</sup> is the unique child of <sup>u</sup><sup>a</sup> on <sup>P</sup>(ub). Since <sup>u</sup>a, u<sup>b</sup> ∈ <sup>P</sup>(θ(<sup>s</sup> −v )), c<sup>a</sup> is also the unique child of u<sup>a</sup> on P(θ(s −v )).

By the Priority dominance condition for wa, we have rw<sup>a</sup> > rc<sup>a</sup> and <sup>w</sup><sup>a</sup> ̸<sup>=</sup> <sup>c</sup>a.

Because w<sup>a</sup> satisfies the condition, Lemma [E.6](#page-16-1) guarantees that during the tokenization of s, immediately prior to executing the rule rw<sup>a</sup> , the rightmost two tokens are exactly u<sup>a</sup> and v. Likewise, immediately prior to executing the rule rw<sup>b</sup> , the rightmost two tokens are exactly u<sup>b</sup> and v.

Because u<sup>a</sup> is a proper ancestor of ub, during the forward tokenization of s, the state where u<sup>a</sup> and v are the rightmost two tokens must strictly precede the state where u<sup>b</sup> and v are the rightmost two tokens.

During the tokenization of s, when executing the rule rw<sup>a</sup> , the token boundary immediately to the left of the last token v must survive the merge; otherwise, the last token would never be v immediately prior to executing the rule rw<sup>b</sup> later on. This means that the execution of rw<sup>a</sup> leaves a mergeable adjacent token pair [ua, v] intact at the end. However, by the left-to-right nature of BPE, this will only occur when the predecessor and the successor of the merge rule are the same, and there is a sequence of at least three such identical tokens being adjacent. Thus, we must have u<sup>a</sup> = v and w<sup>a</sup> is a child of ua.

Hence, immediately prior to executing the rule r<sup>w</sup><sup>a</sup> during the tokenization of s, the rightmost three tokens in the sequence are exactly the same: the token v. After executing the rule r<sup>w</sup><sup>a</sup> , the rightmost two tokens become exactly w<sup>a</sup> and v. Consider the token-wise truncation removing the last token v to obtain the valid tokenization of s −v . At this specific stage, we have w<sup>a</sup> as the last token of the tokenization of s −v , i.e., <sup>w</sup><sup>a</sup> ∈ <sup>P</sup>(θ(<sup>s</sup> −v )).

Since w<sup>a</sup> is a child of ua, w<sup>a</sup> is the unique child of u<sup>a</sup> on P(θ(s −v )), contradicting <sup>w</sup><sup>a</sup> ̸<sup>=</sup> <sup>c</sup>a.

Therefore, the assumption is false.

Claim 3 (The answer node satisfies the condition). Let w = θ(s) be the last token for a non-empty string s after tokenization. Then w satisfies the Prefix Last-Token Condition (Definition [4.1\)](#page-3-0) with respect to s.

*Proof.* If w is an atomic token, it satisfies the condition by definition. Assume w is non-atomic. Let u = pre(w) and <sup>v</sup> = suc(w), with <sup>r</sup><sup>w</sup> being the canonical merge rule (u, v) → <sup>w</sup>.

Since w = θ(s), the tokenization of s eventually produces w as its last token. This implies that immediately prior to the execution of rw, the token sequence of s must end exactly with u and v.

Step 1: Reachability. At this exact moment, the boundary between u and v exists. By Lemma [E.5,](#page-16-3) performing token-wise truncation at this boundary (removing v) yields the valid tokenization of s −v at this stage, which ends with the token u. By Lemma [E.3,](#page-16-0) since u appears as the last token during the tokenization of s −v , we have <sup>u</sup> ∈ <sup>P</sup>(θ(<sup>s</sup> −v )). This establishes the Reachability condition for w.

Step 2: Priority Dominance. Suppose <sup>u</sup> ̸<sup>=</sup> <sup>θ</sup>(<sup>s</sup> −v ). Then the last token u during the tokenization of s <sup>−</sup><sup>v</sup> must eventually be consumed leftward by some merge rule <sup>r</sup><sup>c</sup><sup>u</sup> = (k, u) → <sup>c</sup>u, where <sup>c</sup><sup>u</sup> is the unique child of <sup>u</sup> on <sup>P</sup>(θ(<sup>s</sup> −v )).

Since u appears as the last token, during the tokenization of s −v immediately prior to the execution of rw, the rule r<sup>c</sup><sup>u</sup> has not yet been applied, meaning its priority cannot be strictly higher than <sup>r</sup>w, i.e., <sup>r</sup><sup>c</sup><sup>u</sup> ≤ <sup>r</sup>w.

Suppose their priorities are equal, i.e., c<sup>u</sup> = w. Since r<sup>w</sup> = (u, v) and r<sup>c</sup><sup>u</sup> = (k, u), we must have u = v, making the rule <sup>r</sup><sup>w</sup> = (u, u) → <sup>w</sup>.

Since <sup>u</sup> ̸<sup>=</sup> <sup>θ</sup>(<sup>s</sup> −v ) and c<sup>u</sup> is the unique child of u on P(θ(s −v )), during the tokenization of s <sup>−</sup><sup>v</sup> when applying r<sup>c</sup><sup>u</sup> = rw, the last token must be altered to w in order to form θ(s −v ). However, since w = θ(s), during the tokenization of s when applying rw, the last token must be altered to w. Similar to the proof of Step 2 in Claim 1, this will be impossible. Thus <sup>c</sup><sup>u</sup> ̸<sup>=</sup> <sup>w</sup> and <sup>r</sup><sup>c</sup><sup>u</sup> < rw.

This establishes the Priority Dominance condition for w.

Claim 4 (The answer node has no children satisfying the condition). Let s be a non-empty string. The answer node θ(s) has no children that satisfy the Prefix Last-Token Condition (Definition [4.1\)](#page-3-0) with respect to s.

*Proof.* Let v = θ(s). Assume for contradiction that there exists a child node w of v (meaning v = suc(w)) that satisfies the condition with respect to <sup>s</sup>. Let <sup>u</sup> = pre(w), and let <sup>r</sup><sup>w</sup> be the canonical merge rule (u, v) → <sup>w</sup>.

Because v = θ(s), the Prefix Consistency (Lemma [3.1\)](#page-2-0) guarantees that the final tokenization of s is exactly the tokenization of s −v appended with v, i.e., T(s) = T(s −v ) ⊕ [v].

By the Reachability condition for <sup>w</sup>, we have <sup>u</sup> ∈ <sup>P</sup>(θ(<sup>s</sup> −v )). We consider the two possible cases for u:

Case 1: u = θ(s −v ). If u is exactly the last token of s −v , then T(s −v ) ends with u. Consequently, the final tokenization T(s) must end exactly with the adjacent pair of tokens [u, v]. However, since <sup>r</sup><sup>w</sup> = (u, v) → <sup>w</sup> is a valid merge rule in the vocabulary, the deterministic BPE process would not terminate leaving the matchable pair [u, v] intact. If <sup>u</sup> ̸<sup>=</sup> <sup>v</sup>, the tokenization of s will not terminate with the isolated token v as the last token. Even if u = v, in the final tokenization T(s), the rightmost two tokens would at most be w and v, rather than two adjacent u's, meaning the tokenization T(s −v ) would have w as the last token. Hence, u will not be θ(s −v ).

Case 2: <sup>u</sup> ̸<sup>=</sup> <sup>θ</sup>(<sup>s</sup> −v ). If u is not the last token of s −v , it must eventually be consumed leftward by some merge rule <sup>r</sup><sup>c</sup><sup>u</sup> = (k, u) → <sup>c</sup>u, where <sup>c</sup><sup>u</sup> is the unique child of <sup>u</sup> on <sup>P</sup>(θ(<sup>s</sup> −v )). Because w satisfies the condition, the Priority dominance strictly dictates that r<sup>w</sup> > r<sup>c</sup><sup>u</sup> .

During the tokenization of the string s, since v = θ(s), the suffix token v must never be consumed by any rightward merges after its formation. So the token boundary immediately to the left of the suffix v is never eliminated. By Lemma [E.4,](#page-16-2) we can truncate the tokenization of s removing the suffix corresponding to the string v and obtain the valid tokenization of s −v after the execution of each merge rule.

Consider the tokenizations of both s −v and s immediately prior to executing rw, where the tokens u and v have been formed, as they are the predecessor and the successor of w. At this stage, r<sup>c</sup><sup>u</sup> has not been executed since r<sup>w</sup> > r<sup>c</sup><sup>u</sup> . Hence, at this moment, the last token of the tokenization of s −v is u, and the last token of the tokenization of s is v. So the rightmost two tokens of the tokenization of s are u and v.

However, since v = θ(s), the execution of r<sup>w</sup> must skip the rightmost adjacent u and v, which is only possible when u = v. Similar to the proof of Step 2 in Claim 1, this will also be impossible, as it leads to the case where w = cu, directly contradicting the requirement of Priority dominance (r<sup>w</sup> > r<sup>c</sup><sup>u</sup> ).

Conclusion. Both cases yield a direct contradiction. Therefore, the assumption is false, and the answer node θ(s) has no children satisfying the condition.

Conclusion of the Proof. We now conclude the proof of Theorem [4.2.](#page-4-1) Claim 1 establishes that the Prefix Last-Token Condition is upward closed along successor edges. Claim 2 shows that for any node, at most one child can satisfy the condition. Claim 3 guarantees that the true last token θ(s) does satisfy the condition, while Claim 4 shows that it is maximal and admits no further extension.

Together, these four claims imply that the set of tokens in SufSucTree(t) satisfying the Prefix Last-Token Condition forms exactly a single, maximal path from θ(s) to the root of the tree. This completes the proof.

# <span id="page-20-0"></span>F. Square-Root Tiled Transition Table

In an Aho–Corasick automaton [\(Aho & Corasick,](#page-8-1) [1975\)](#page-8-1), a straightforward implementation stores a full transition array over the alphabet Σ for every state, yielding constant-time transitions at the cost of a large memory footprint.

A key observation is that, for any state, its transition table differs from that of its suffix link only at entries corresponding to outgoing trie edges. This structural locality allows transitions to be shared persistently across states.

We exploit this property using a square-root tiling of the alphabet. The alphabet is partitioned into fixed-size tiles; each state stores references to its tiles, and a tile is duplicated only when a transition within it is modified. As a result, most tiles are shared between a state and its suffix link, while updates remain local to the affected tiles.

This representation preserves O(1) transition queries and supports efficient construction, while substantially reducing memory usage in practice.

# <span id="page-21-0"></span>G. Eager Output Algorithm Details

Based on the Active Frontier definition in Section [6.1,](#page-6-1) we maintain the subgraph of the Prefix Tree of Tokens composed of the nodes in P and their ancestors to identify the common ancestral path. The algorithm proceeds as follows:

- 1. Window Maintenance: We maintain P using two pointers. The right pointer adds the new <sup>θ</sup>(s). The left pointer advances to satisfy the bound |s| − <sup>d</sup>(s), removing expired tokens, where the function <sup>d</sup> is defined in Section [6.1.](#page-6-1)
- 2. Subgraph Tracking: We maintain the nodes in P and their ancestors as a dynamic subgraph. For each node in this subgraph, we record the number of its children that are also part of the subgraph.
- 3. Eager Emission: We maintain the children of the virtual root. If the virtual root has exactly one child c in the subgraph, it implies that all Parental Candidates (and thus all possible futures) are descendants of the node c. The token represented by c is therefore stable. We emit the corresponding token, update the virtual root to c, and repeat the check.

Each node in the Prefix Tree of Tokens is inserted into the maintained subgraph exactly once, at the moment when the right pointer includes the corresponding last token into P. A node may persist in the subgraph even after it ceases to belong to P, but it will be removed at most once, when it no longer lies on the ancestral path of any active Parental Candidate.

During the advancement of the left pointer, each step removes either one node from the subgraph or performs a constant amount of bookkeeping without removal. Consequently, each node contributes O(1) work over the entire execution of the algorithm.

Therefore, the eager output mechanism incurs an amortized O(1) time overhead per input update.

# <span id="page-21-1"></span>H. Detailed Benchmarks

## H.1. Experiment Setup

All benchmarks were conducted on a bare-metal server equipped with an Intel® Xeon® Platinum 8362 CPU @ 2.80GHz. To ensure reproducibility and minimize measurement noise, we applied the following configurations:

- CPU Isolation: Experiments were pinned to a single NUMA node (Node 1) containing 32 physical cores and 128 GB of RAM.
- System Tuning: Hyper-threading (SMT), Turbo Boost, and Address Space Layout Randomization (ASLR) were disabled.
- Concurrency: Tests were executed using 30 parallel workers. Each worker ran as an isolated, single-threaded process that independently loaded the tokenizer and dataset.

To ensure the validity of our results, we verified the correctness of our implementations against baseline methods prior to performance benchmarking. For all benchmarks (tokenizers and tiktoken bindings), we changed the global allocator to mimalloc [\(Leijen et al.,](#page-9-9) [2019;](#page-9-9) [Purplecoin,](#page-10-5) [2026\)](#page-10-5) and fixed seeds for hash functions to guarantee stable and reproducible latency measurements.

## H.2. Datasets

We constructed three representative datasets using specific subsets of publicly available datasets. Table [2](#page-22-0) provides a summary of the dataset statistics.

The specific sampling strategies were as follows:

- English & Chinese: We utilized the first Parquet shard from the standard training split of the Wikipedia dataset (20231101 dump), and employed a strided sampling strategy, extracting every 42nd document for English and every 60th document for Chinese.

*Table 2.* Datasets used in experiments.

<span id="page-22-0"></span>

| Name    | (Reference) |             |        | Repository |             |       | #Documents | Total #Bytes |
|---------|-------------|-------------|--------|------------|-------------|-------|------------|--------------|
| English | (Wikimedia  | Foundation, | 2023a) | Wikimedia  | Foundation, | 2023b | 3,722      | 16,522,972   |
| Chinese | (Wikimedia  | Foundation, | 2023a) | Wikimedia  | Foundation, | 2023b | 3,847      | 16,337,583   |
| Code    | (Together   | Computer,   | 2023a) | Together   | Computer,   | 2023b | 2,500      | 16,803,408   |

- Code: We extracted data from the RedPajama GitHub subset [\(Together Computer,](#page-10-9) [2023b\)](#page-10-9), specifically using the file with the filename "filtered\_08cdfa755e6d4d89b673d5bd1acee5f6.sampled.jsonl". We selected the first 2,500 documents from this file.

Additionally, for pathological input analysis, we constructed strings consisting of 2 k repetitions of the character 'a'.

## H.3. Tokenizers

<span id="page-22-1"></span>We evaluated a diverse set of tokenizers supported by two major libraries: Hugging Face's tokenizers and OpenAI's tiktoken.

*Table 3.* Tokenizers used in experiments for Hugging Face's **tokenizers**.

| Name         | (Reference) |               |        | Repository   |        |       | Vocab Size P99 | Token Length |
|--------------|-------------|---------------|--------|--------------|--------|-------|----------------|--------------|
| CodeLlama    | (Meta       | AI,           | 2023)  | Meta         | Llama, | 2023  | 32,016         | 12           |
| DeepSeek-3.2 |             | (DeepSeek-AI, | 2025a) | DeepSeek-AI, |        | 2025b | 128,000        | 15           |
| Gemma-3      | †           |               |        |              |        |       |                |              |
|              | (Google,    |               | 2025a) | Google,      | 2025b  |       | 262,144        | 14           |
| GPT-OSS      | (OpenAI,    |               | 2025a) | OpenAI,      | 2025b  |       | 199,998        | 19           |
| Llama-3.1    | *           |               |        |              |        |       |                |              |
|              | (Meta       | AI,           | 2024)  | Meta         | Llama, | 2024  | 128,000        | 17           |
| Llama-4      | (Meta       | AI, 2025)     |        | Meta         | Llama, | 2025  | 200,000        | 21           |
| Mistral-3    | (Mistral    | AI,           | 2025a) | Mistral      | AI,    | 2025b | 131,072        | 16           |
| Ouro         | (ByteDance, | 2025a)        |        | ByteDance,   |        | 2025b | 49,152         | 14           |
| Qwen-3       | (Qwen       | Team,         | 2025a) | Qwen         | Team,  | 2025b | 151,643        | 18           |

Improper dictionary. See Appendix [A.6](#page-13-1) for non-properizable cases. \* Properized dictionary. See Appendix [A](#page-11-0) for properization.

Hugging Face Models. Table [3](#page-22-1) summarizes the open-source tokenizers selected for our experiments. These models exhibit varying pre-tokenization strategies:

- Regex-Based: The majority of the models (DeepSeek-3.2, GPT-OSS, Llama-3.1, Llama-4, Mistral-3, and Qwen-3) employ regex-based rules to split input text before tokenization.
- Rule-Based: Ouro utilizes a digit-based pre-tokenization, and Gemma-3 employs a rule on space characters.
- None: Notably, CodeLlama applies no pre-tokenization logic.

Regarding the "properness" of dictionaries, the improper merge rules of Llama-3.1 are properized for our benchmarks (see Appendix [A\)](#page-11-0). In contrast, Gemma-3's merge rules are improper and cannot be properized (see Appendix [A.6\)](#page-13-1).

OpenAI Models. For the tiktoken library, we utilized the standard built-in encoding models. Table [4](#page-23-1) lists the specific models that we used. Note that all tested tiktoken models employ regex-based pre-tokenization.

## H.4. Detailed Results

We report throughput in terms of MiB/s based on the median of multiple execution runs. For each benchmark setting, throughput is computed as the total number of input bytes divided by the sum of the per-document median execution times. This aggregation reflects the effective end-to-end processing rate under repeated, independent tokenization workloads.

*Table 4.* Tokenizers used in experiments for OpenAI's **tiktoken**.

<span id="page-23-1"></span>

| Name   | Code   | Name | Vocab Size P99 | Token Length |
|--------|--------|------|----------------|--------------|
| CL100K | cl100k | base | 100,256        | 16           |
| O200K  | o200k  | base | 199,998        | 19           |
| P50K   | p50k   | base | 50,280         | 14           |
| R50K   | r50k   | base | 50,256         | 14           |

We evaluate two input regimes, indicated by the Eval column in Table [5.](#page-23-0) In the concat setting, all documents in a dataset are concatenated into a single input stream, separated by newline characters, and tokenized as one continuous sequence. In the per-doc setting, each document is provided to the tokenizer as an independent input, and execution times are measured separately per document before aggregation. The results reported in the main text (Table [1\)](#page-7-0) correspond to the concat setting, while Table [5](#page-23-0) provides the full breakdown across both evaluation regimes.

<span id="page-23-0"></span>*Table 5.* Detailed throughput benchmarks. Base: Original built-in BPE implementation. Inc: Our incremental BPE. Eager: "Inc" with eager output. I/B: Relative speedup of Inc/Base.

| Dataset Hugging | Eval Face’s | Tokenizer tokenizers | Cache | Base (MiB/s) |    | Inc (MiB/s) |    | Eager (MiB/s) | I/B ( × ) |
|-----------------|-------------|----------------------|-------|--------------|----|-------------|----|---------------|-----------|
| English         | concat      | CodeLlama            | ✔ 0   | 80           | 2  | 49          | 2  | 23            | 3.13      |
| English         | concat      | CodeLlama            | ✘ 0   | 80           | 2  | 45          | 2  | 19            | 3.05      |
| English         | concat      | DeepSeek-3.2         | ✔ 1   | 52           | 1  | 54          | 1  | 51            | 1.01      |
| English         | concat      | DeepSeek-3.2         | ✘ 1   | 42           | 1  | 48          | 1  | 44            | 1.04      |
| English         | concat      | GPT-OSS              | ✔ 1   | 89           | 1  | 90          | 1  | 88            | 1 00      |
| English         | concat      | GPT-OSS              | ✘ 1   | 89           | 1  | 92          | 1  | 89            | 1.01      |
| English         | concat      | Llama-3.1            | ✔ 1   | 84           | 1  | 82          | 1  | 79            | 0 99      |
| English         | concat      | Llama-3.1            | ✘ 1   | 87           | 1  | 87          | 1  | 85            | 1 00      |
| English         | concat      | Llama-4              | ✔ 1   | 84           | 1  | 86          | 1  | 84            | 1.01      |
| English         | concat      | Llama-4              | ✘ 1   | 86           | 1  | 88          | 1  | 85            | 1.01      |
| English         | concat      | Mistral-3            | ✔ 1   | 83           | 1  | 83          | 1  | 80            | 1 00      |
| English         | concat      | Mistral-3            | ✘ 1   | 84           | 1  | 83          | 1  | 80            | 0 99      |
| English         | concat      | Ouro                 | ✔ 1   | 59           | 1  | 59          | 1  | 56            | 1 00      |
| English         | concat      | Ouro                 | ✘ 1   | 51           | 1  | 57          | 1  | 50            | 1.04      |
| English         | concat      | Qwen-3               | ✔ 1   | 52           | 1  | 59          | 1  | 54            | 1.05      |
| English         | concat      | Qwen-3               | ✘ 1   | 34           | 1  | 50          | 1  | 45            | 1.12      |
| OpenAI’s        | tiktoken    |                      |       |              |    |             |    |               |           |
| English         | concat      | CL100K               | — 11  | 17           | 10 | 78          | 10 | 03            | 0 96      |
| English         | concat      | O200K                | — 6   | 21           | 6  | 12          | 5  | 98            | 0 99      |
| English         | concat      | P50K                 | — 12  | 86           | 12 | 42          | 11 | 45            | 0 97      |
| English         | concat      | R50K                 | — 12  | 83           | 12 | 38          | 11 | 49            | 0 96      |
| Hugging         | Face’s      | tokenizers           |       |              |    |             |    |               |           |
| English         | per-doc     | CodeLlama            | ✔ 2   | 59           | 3  | 87          | 3  | 20            | 1.49      |
| English         | per-doc     | CodeLlama            | ✘ 2   | 59           | 3  | 89          | 3  | 20            | 1.50      |
| English         | per-doc     | DeepSeek-3.2         | ✔ 2   | 04           | 2  | 15          | 2  | 09            | 1.05      |
| English         | per-doc     | DeepSeek-3.2         | ✘ 1   | 83           | 2  | 04          | 1  | 91            | 1.11      |
| English         | per-doc     | GPT-OSS              | ✔ 2   | 78           | 2  | 80          | 2  | 73            | 1.01      |
| English         | per-doc     | GPT-OSS              | ✘ 2   | 77           | 2  | 81          | 2  | 75            | 1.01      |
| English         | per-doc     | Llama-3.1            | ✔ 2   | 74           | 2  | 78          | 2  | 71            | 1.01      |
| English         | per-doc     | Llama-3.1            | ✘ 2   | 78           | 2  | 81          | 2  | 72            | 1.01      |
| English         | per-doc     | Llama-4              | ✔ 2   | 67           | 2  | 74          | 2  | 66            | 1.03      |

*Table 5.* Detailed throughput benchmarks for Hugging Face's **tokenizers**.

| Dataset  | Eval     | Tokenizer    | Cache | Base (MiB/s) |    | Inc (MiB/s) |    | Eager (MiB/s) | I/B ( × ) |
|----------|----------|--------------|-------|--------------|----|-------------|----|---------------|-----------|
| English  | per-doc  | Llama-4      | ✘ 2   | 66           | 2  | 77          | 2  | 74            | 1.04      |
| English  | per-doc  | Mistral-3    | ✔ 2   | 67           | 2  | 73          | 2  | 65            | 1.02      |
| English  | per-doc  | Mistral-3    | ✘ 2   | 71           | 2  | 79          | 2  | 71            | 1.03      |
| English  | per-doc  | Ouro         | ✔ 2   | 26           | 2  | 29          | 2  | 21            | 1.01      |
| English  | per-doc  | Ouro         | ✘ 2   | 05           | 2  | 18          | 2  | 06            | 1.07      |
| English  | per-doc  | Qwen-3       | ✔ 1   | 99           | 2  | 20          | 2  | 12            | 1.10      |
| English  | per-doc  | Qwen-3       | ✘ 1   | 67           | 2  | 08          | 1  | 95            | 1.25      |
| OpenAI’s | tiktoken |              |       |              |    |             |    |               |           |
| English  | per-doc  | CL100K       | — 11  | 54           | 11 | 19          | 10 | 35            | 0 97      |
| English  | per-doc  | O200K        | — 6   | 30           | 6  | 23          | 5  | 99            | 0 99      |
| English  | per-doc  | P50K         | — 13  | 43           | 12 | 98          | 11 | 98            | 0 97      |
| English  | per-doc  | R50K         | — 13  | 43           | 12 | 99          | 11 | 90            | 0 97      |
| Hugging  | Face’s   | tokenizers   |       |              |    |             |    |               |           |
| Chinese  | concat   | CodeLlama    | ✔ 2   | 33           | 2  | 55          | 2  | 47            | 1.10      |
| Chinese  | concat   | CodeLlama    | ✘ 2   | 33           | 2  | 54          | 2  | 46            | 1.09      |
| Chinese  | concat   | DeepSeek-3.2 | ✔ 1   | 52           | 1  | 41          | 1  | 32            | 0 93      |
| Chinese  | concat   | DeepSeek-3.2 | ✘ 1   | 55           | 1  | 41          | 1  | 33            | 0 91      |
| Chinese  | concat   | GPT-OSS      | ✔ 1   | 71           | 1  | 84          | 1  | 73            | 1.08      |
| Chinese  | concat   | GPT-OSS      | ✘ 1   | 73           | 1  | 85          | 1  | 74            | 1.07      |
| Chinese  | concat   | Llama-3.1    | ✔ 1   | 79           | 1  | 86          | 1  | 75            | 1.03      |
| Chinese  | concat   | Llama-3.1    | ✘ 1   | 84           | 1  | 90          | 1  | 79            | 1.03      |
| Chinese  | concat   | Llama-4      | ✔ 1   | 73           | 1  | 75          | 1  | 63            | 1.01      |
| Chinese  | concat   | Llama-4      | ✘ 1   | 75           | 1  | 79          | 1  | 67            | 1.02      |
| Chinese  | concat   | Mistral-3    | ✔ 1   | 73           | 1  | 80          | 1  | 71            | 1.04      |
| Chinese  | concat   | Mistral-3    | ✘ 1   | 75           | 1  | 82          | 1  | 72            | 1.04      |
| Chinese  | concat   | Ouro         | ✔ 1   | 48           | 1  | 51          | 1  | 48            | 1.02      |
| Chinese  | concat   | Ouro         | ✘ 1   | 51           | 1  | 53          | 1  | 49            | 1.01      |
| Chinese  | concat   | Qwen-3       | ✔ 1   | 59           | 1  | 65          | 1  | 54            | 1.04      |
| Chinese  | concat   | Qwen-3       | ✘ 1   | 58           | 1  | 65          | 1  | 55            | 1.04      |
| OpenAI’s | tiktoken |              |       |              |    |             |    |               |           |
| Chinese  | concat   | CL100K       | — 9   | 36           | 14 | 92          | 11 | 71            | 1.59      |
| Chinese  | concat   | O200K        | — 7   | 10           | 10 | 39          | 8  | 63            | 1.46      |
| Chinese  | concat   | P50K         | — 10  | 03           | 13 | 57          | 10 | 98            | 1.35      |
| Chinese  | concat   | R50K         | — 10  | 01           | 13 | 55          | 10 | 95            | 1.35      |
| Hugging  | Face’s   | tokenizers   |       |              |    |             |    |               |           |
| Chinese  | per-doc  | CodeLlama    | ✔ 4   | 30           | 4  | 69          | 4  | 37            | 1.09      |
| Chinese  | per-doc  | CodeLlama    | ✘ 4   | 33           | 4  | 71          | 4  | 45            | 1.09      |
| Chinese  | per-doc  | DeepSeek-3.2 | ✔ 1   | 94           | 1  | 76          | 1  | 60            | 0 91      |
| Chinese  | per-doc  | DeepSeek-3.2 | ✘ 1   | 96           | 1  | 77          | 1  | 62            | 0 91      |
| Chinese  | per-doc  | GPT-OSS      | ✔ 2   | 25           | 2  | 41          | 2  | 22            | 1.07      |
| Chinese  | per-doc  | GPT-OSS      | ✘ 2   | 28           | 2  | 46          | 2  | 25            | 1.08      |
| Chinese  | per-doc  | Llama-3.1    | ✔ 2   | 47           | 2  | 54          | 2  | 31            | 1.03      |
| Chinese  | per-doc  | Llama-3.1    | ✘ 2   | 51           | 2  | 58          | 2  | 34            | 1.03      |
| Chinese  | per-doc  | Llama-4      | ✔ 2   | 20           | 2  | 28          | 2  | 06            | 1.04      |
| Chinese  | per-doc  | Llama-4      | ✘ 2   | 26           | 2  | 30          | 2  | 09            | 1.02      |
| Chinese  | per-doc  | Mistral-3    | ✔ 2   | 31           | 2  | 44          | 2  | 22            | 1.06      |
| Chinese  | per-doc  | Mistral-3    | ✘ 2   | 34           | 2  | 48          | 2  | 27            | 1.06      |
| Chinese  | per-doc  | Ouro         | ✔ 2   | 19           | 2  | 25          | 2  | 17            | 1.03      |

*Continued on next page...*

*Table 5.* Detailed throughput benchmarks for Hugging Face's **tokenizers**.

| Dataset  | Eval     | Tokenizer    | Cache | Base (MiB/s) |    | Inc (MiB/s) |    | Eager (MiB/s) | I/B ( × ) |
|----------|----------|--------------|-------|--------------|----|-------------|----|---------------|-----------|
| Chinese  | per-doc  | Ouro         | ✘ 2   | 23           | 2  | 30          | 2  | 20            | 1.03      |
| Chinese  | per-doc  | Qwen-3       | ✔ 2   | 00           | 2  | 15          | 1  | 93            | 1.08      |
| Chinese  | per-doc  | Qwen-3       | ✘ 1   | 97           | 2  | 15          | 1  | 94            | 1.09      |
| OpenAI’s | tiktoken |              |       |              |    |             |    |               |           |
| Chinese  | per-doc  | CL100K       | — 9   | 75           | 16 | 00          | 12 | 37            | 1.64      |
| Chinese  | per-doc  | O200K        | — 7   | 37           | 11 | 09          | 9  | 09            | 1.50      |
| Chinese  | per-doc  | P50K         | — 10  | 56           | 14 | 50          | 11 | 52            | 1.37      |
| Chinese  | per-doc  | R50K         | — 10  | 55           | 14 | 45          | 11 | 46            | 1.37      |
| Hugging  | Face’s   | tokenizers   |       |              |    |             |    |               |           |
| Code     | concat   | CodeLlama    | ✔ 0   | 82           | 2  | 37          | 2  | 21            | 2.88      |
| Code     | concat   | CodeLlama    | ✘ 0   | 81           | 2  | 34          | 2  | 17            | 2.87      |
| Code     | concat   | DeepSeek-3.2 | ✔ 1   | 52           | 1  | 56          | 1  | 54            | 1.03      |
| Code     | concat   | DeepSeek-3.2 | ✘ 1   | 45           | 1  | 54          | 1  | 48            | 1.07      |
| Code     | concat   | GPT-OSS      | ✔ 1   | 86           | 1  | 88          | 1  | 87            | 1.01      |
| Code     | concat   | GPT-OSS      | ✘ 1   | 88           | 1  | 88          | 1  | 87            | 1 00      |
| Code     | concat   | Llama-3.1    | ✔ 1   | 78           | 1  | 80          | 1  | 78            | 1.02      |
| Code     | concat   | Llama-3.1    | ✘ 1   | 82           | 1  | 86          | 1  | 82            | 1.02      |
| Code     | concat   | Llama-4      | ✔ 1   | 84           | 1  | 85          | 1  | 83            | 1 00      |
| Code     | concat   | Llama-4      | ✘ 1   | 86           | 1  | 85          | 1  | 83            | 0 99      |
| Code     | concat   | Mistral-3    | ✔ 1   | 80           | 1  | 79          | 1  | 78            | 0 99      |
| Code     | concat   | Mistral-3    | ✘ 1   | 79           | 1  | 80          | 1  | 79            | 1.01      |
| Code     | concat   | Ouro         | ✔ 1   | 53           | 1  | 57          | 1  | 54            | 1.02      |
| Code     | concat   | Ouro         | ✘ 1   | 48           | 1  | 55          | 1  | 50            | 1.05      |
| Code     | concat   | Qwen-3       | ✔ 1   | 54           | 1  | 65          | 1  | 62            | 1.08      |
| Code     | concat   | Qwen-3       | ✘ 1   | 38           | 1  | 59          | 1  | 54            | 1.15      |
| OpenAI’s | tiktoken |              |       |              |    |             |    |               |           |
| Code     | concat   | CL100K       | — 8   | 16           | 8  | 50          | 7  | 96            | 1.04      |
| Code     | concat   | O200K        | — 5   | 49           | 5  | 51          | 5  | 41            | 1 00      |
| Code     | concat   | P50K         | — 8   | 29           | 8  | 90          | 8  | 05            | 1.07      |
| Code     | concat   | R50K         | — 8   | 43           | 8  | 85          | 8  | 01            | 1.05      |
| Hugging  | Face’s   | tokenizers   |       |              |    |             |    |               |           |
| Code     | per-doc  | CodeLlama    | ✔ 2   | 11           | 3  | 62          | 3  | 17            | 1.72      |
| Code     | per-doc  | CodeLlama    | ✘ 2   | 11           | 3  | 62          | 3  | 16            | 1.72      |
| Code     | per-doc  | DeepSeek-3.2 | ✔ 1   | 94           | 2  | 04          | 1  | 98            | 1.06      |
| Code     | per-doc  | DeepSeek-3.2 | ✘ 1   | 81           | 2  | 00          | 1  | 91            | 1.11      |
| Code     | per-doc  | GPT-OSS      | ✔ 2   | 37           | 2  | 41          | 2  | 38            | 1.01      |
| Code     | per-doc  | GPT-OSS      | ✘ 2   | 45           | 2  | 51          | 2  | 47            | 1.02      |
| Code     | per-doc  | Llama-3.1    | ✔ 2   | 36           | 2  | 46          | 2  | 38            | 1.04      |
| Code     | per-doc  | Llama-3.1    | ✘ 2   | 43           | 2  | 51          | 2  | 43            | 1.03      |
| Code     | per-doc  | Llama-4      | ✔ 2   | 36           | 2  | 37          | 2  | 37            | 1.01      |
| Code     | per-doc  | Llama-4      | ✘ 2   | 30           | 2  | 37          | 2  | 33            | 1.03      |
| Code     | per-doc  | Mistral-3    | ✔ 2   | 30           | 2  | 36          | 2  | 32            | 1.03      |
| Code     | per-doc  | Mistral-3    | ✘ 2   | 34           | 2  | 41          | 2  | 36            | 1.03      |
| Code     | per-doc  | Ouro         | ✔ 2   | 01           | 2  | 08          | 2  | 02            | 1.03      |
| Code     | per-doc  | Ouro         | ✘ 1   | 87           | 2  | 01          | 1  | 93            | 1.07      |
| Code     | per-doc  | Qwen-3       | ✔ 1   | 84           | 2  | 08          | 2  | 02            | 1.13      |
| Code     | per-doc  | Qwen-3       | ✘ 1   | 64           | 2  | 03          | 1  | 92            | 1.24      |
| OpenAI’s | tiktoken |              |       |              |    |             |    |               |           |

*Continued on next page...*

*Table 5.* Detailed throughput benchmarks for Hugging Face's **tokenizers**.

| Dataset | Eval    | Tokenizer | Cache | Base (MiB/s) |   | Inc (MiB/s) |   | Eager (MiB/s) | I/B ( × ) |
|---------|---------|-----------|-------|--------------|---|-------------|---|---------------|-----------|
| Code    | per-doc | CL100K    | — 8   | 35           | 8 | 76          | 8 | 19            | 1.05      |
| Code    | per-doc | O200K     | — 5   | 58           | 5 | 64          | 5 | 43            | 1.01      |
| Code    | per-doc | P50K      | — 8   | 54           | 9 | 25          | 8 | 31            | 1.08      |
| Code    | per-doc | R50K      | — 8   | 66           | 9 | 18          | 8 | 21            | 1.06      |

# <span id="page-26-0"></span>I. Profiling Analysis of Tokenization Pipelines

To better understand the system-level bottlenecks in existing tokenization pipelines, we profile the execution using Linux perf and visualize the results with inferno [\(Gjengset,](#page-9-21) [2026\)](#page-9-21). All flame graphs are collected from end-to-end tokenization runs, including normalization, pre-tokenization, and BPE, under the same configurations as the benchmark experiments in the main text.

For clarity of presentation, we apply light post-processing to the raw call stacks. Specifically, we retain only frames corresponding to the tokenization pipeline, truncate excessively deep stacks, and strip type and template information, preserving only function-level symbols and the structural hierarchy of call stacks. These transformations preserve the relative time distribution across pipeline stages while improving readability.

<span id="page-26-1"></span>![](_page_26_Figure_6.jpeg)

*Figure 5.* Flame graph of **tokenizers** (Qwen-3) execution with our incremental non-eager implementation on the Code dataset. The BPE merge phase (tokenize without cache) accounts for only 13.11% of the total execution time. The remaining time is dominated by normalization, pre-tokenization, and result construction cost (e.g., cloning token strings).

<span id="page-26-2"></span>![](_page_26_Figure_8.jpeg)

*Figure 6.* Flame graph of **tiktoken** (O200K) execution with our incremental non-eager implementation on the Code dataset. The regex matching phase (dominated by find from pos with option flags and run) consumes approximately 80.25% of the total CPU time. In contrast, the actual BPE merge phase (byte pair encode on the left) accounts for only 6.45%. This indicates that, under this configuration, the pre-tokenization guardrail imposes a computational overhead exceeding 12× the cost of the core BPE merge stage.

Figure [5](#page-26-1) presents a representative flame graph for Hugging Face's tokenizers library with the tokenizer Qwen-3, using our incremental non-eager BPE implementation on the Code dataset. The BPE merge phase itself (tokenize without cache) constitutes a minor fraction of the total runtime, highlighting that, in this pipeline, the overall throughput is primarily constrained by non-BPE components.

<span id="page-27-1"></span>![](_page_27_Figure_1.jpeg)

*Figure 7.* Flame graphs of **tiktoken** using the original baseline implementation under pathological inputs with lengths from 2 to 2 . The BPE merge phase (byte pair encode on the left) becomes increasingly dominant as the input length grows, consistent with its O(n 2 ) time complexity, while the relative contribution of regex matching diminishes.

Figure [6](#page-26-2) profiles tiktoken (O200K) when replacing its BPE stage with our incremental non-eager implementation on the Code dataset. It highlights that the bottleneck shifts to regex-based pre-tokenization, even when the BPE merge phase itself is asymptotically efficient.

Figure [7](#page-27-1) profiles the original tiktoken baseline under pathological inputs of increasing length. As the input size grows, the BPE merge phase increasingly dominates the execution time, providing a fine-grained explanation for the throughput trends reported in Figure [3.](#page-7-1) These pathological inputs are not intended to model realistic workloads, but to isolate and stress-test the asymptotic behavior of the BPE merge stage.

# <span id="page-27-0"></span>J. Comparison with Other Incremental BPE Implementations

In this section, we provide a detailed theoretical and empirical comparison between our algorithm and other existing incremental BPE implementations in Rust, specifically those found in the crate bpe of the GitHub repository rust-gems [\(GitHub,](#page-9-6) [2026\)](#page-9-6).

For the discussion about time and space complexity, let Σ be the size of the alphabet, n be the input length, m the vocabulary size, t<sup>i</sup> the length of the i-th token, and t the maximum token length.

Within rust-gems, there are three main implementations of BPE as the methods of the structure BytePairEncoding. The encode via bitfield method utilizes a binary heap and does not support incremental processing, placing it outside the scope of discussion. The remaining two methods, encode via table and encode via backtracking, support incremental tokenization and are analyzed in the following.

All empirical tests and evaluations were performed by directly replacing the core BPE implementation in the tiktoken [\(OpenAI,](#page-9-2) [2026b\)](#page-9-2) library. The tests were conducted on a Virtual Private Server (VPS), utilizing 8 cores of an Intel® Xeon® Gold 6448Y CPU situated on a single NUMA node, alongside a 16 GB slice of RAM.

## J.1. Theoretical Time Complexity

Both encode via table and encode via backtracking rely on a core underlying function: is valid token pair. This function checks whether two tokens can be placed adjacently, ensuring that applying BPE to their concatenated string yields exactly the same two tokens.

Assuming the "last token" of a string is determined, if a new token can be validly placed adjacent to it, the "last token" of the newly formed string should exactly be this new token.

The validation process takes two tokens, iteratively un-merges either the first token to its successor or the second token to its predecessor according to the rule with the lower priority, and verifies if the token boundary survives. This verification takes O(t) time. Although it can be pre-computed or cached to achieve O(1) query time, the table will be O(m<sup>2</sup> ), which may not be preferable for production.

Method 1: **encode via table** This method processes the tokenization with an Aho–Corasick automaton. At each step, it iterates through the matching suffix tokens from longest to shortest for the current prefix, validating each suffix token via is valid token pair.

- Complexity: In the "best" case scenario, where the longest match is always the correct last token, it still requires at least one validation per step, yielding a lower bound of Ω(n) checks. In the worst case, all suffix tokens must be checked, resulting in O(nt<sup>2</sup> ) time complexity.
- Eager Output: Because this method maintains the prefix tree of tokens essentially, it can theoretically be adapted to support our proposed eager output mechanism.

Method 2: **encode via backtracking** This method employs a greedy strategy. It attempts to find the longest token among the prefixes of the un-tokenized string suffix, verifying it against the currently maintained token sequence via is valid token pair. During the tokenization, it maintains a bit-field to record the positions that cause backtracking to avoid re-computation.

It is notable that the algorithm will backtrack if the current token sequence corresponds to a path from a leaf to the root in the prefix tree of tokens, which indicates no subsequent prefix token will form a valid sequence.

- Complexity: In the "best" case, where the greedy choice is always correct, the validation cost is amortized over the token length, yielding Ω(n). However, in the worst case, whenever the algorithm backtracks, it incurs the cost of validating all possible prefix tokens with the last token, yielding O(nt<sup>2</sup> ).
- Eager Output: As the algorithm is greedy, there is no trivial way to apply our eager output mechanism to this implementation.

<span id="page-28-0"></span>Table [6](#page-28-0) summarizes the complexity of these methods alongside our proposed algorithm. Our method incorporates a simple optimization where we first verify the longest suffix token before traversing the Suffix-Successor Tree, ensuring our "best" case also achieves an Ω(n) lower bound.

*Table 6.* Overall complexity and feature comparison.

| Method |                  | Worst-Case  | “Best”-Case | Eager Output |
|--------|------------------|-------------|-------------|--------------|
| encode | via table        | O ( nt 2    |             |              |
|        |                  | )           | Ω( n )      |              |
|        |                  |             | †           | Yes          |
| encode | via backtracking | O ( nt 2    |             |              |
|        |                  | )           | Ω( n )      | No           |
| Ours   |                  | O ( n log 2 |             |              |
|        |                  | t )         | Ω( n )      | Yes          |

† Assume Ω(1) time for each check.

## J.2. Constructed Pathological Case

To approach the worst-case complexity, we designed an adversarial corner case. This construction deliberately traps algorithms relying on greedy or longest-prefix matching into massive validation and backtracking cycles.

First, to achieve a merge depth of K = 4096, we expand the base alphabet from single bytes to 2-byte pairs. To strictly prevent accidental cross-boundary merges, we construct base tokens <sup>B</sup>1, B2, . . . , B<sup>K</sup> from B:

---

$$\mathcal{B} = \{(i, j) \mid i, j \in \{0, 1, \dots, 255\}, i < j\}.$$

The structural constraint of B guarantees that placing any two base tokens adjacent to each other will not trigger unintended cross-boundary merges.

Next, using these <sup>K</sup> distinct base tokens, we construct a sequence S of <sup>4</sup><sup>K</sup> bytes:

$$\mathcal{S} = B_1 \cdots B_K B_K \cdots B_1$$
.

We then strategically assign merge rule priorities to establish the trap: the absolute highest priority is assigned to the rule merging the two identical tokens located exactly at the sequence center, i.e., (BK, BK). Subsequently, we inject deep nested merge rules originating from the center towards the two ends, i.e.:

| $(B_{K-1}, B_K), (B_{K-2}, B_{K-1}B_K), \dots$ | and | $(B_K, B_{K-1}), (B_K B_{K-1}, B_{K-2}), \dots$ |
|------------------------------------------------|-----|-------------------------------------------------|
|                                                |     |                                                 |

establishing a merge depth of O(K).

The input string is constructed as a concatenation of 128 repetitions of S. Under this pathological input, our method, with worst-case time complexity guarantees, required 37 ms to tokenize the sequence. In stark contrast, encode via table and encode via backtracking required 15.3 s and 23.9 s, respectively.

### J.3. Space Complexity

Initialization Our implementation utilizes a Square-Root Tiled Transition Table for O(1) transitions (detailed in Appendix [F\)](#page-20-0), requiring Θ(√ Σ) space per state. In contrast, rust-gems uses a double-array implementation of Aho-Corasick automata [\(Kanda et al.,](#page-9-22) [2023\)](#page-9-22), which performs transitions in O(1) time and normally requires O(1) space per state, but potentially up to O(Σ) in the worst case.

Additionally, our method requires pre-computing a Centroid Search Tree based on Centroid Decomposition for each Suffix-Successor Tree, leading to an initialization space complexity of O( <sup>P</sup>ti) = O(mt). rust-gems requires no more than O(m) auxiliary space.

Tokenization and Eager Output During standard non-eager tokenization, both our method and the rust-gems implementations require O(n) space to record the token sequence.

However, space complexity behavior differs when applying our eager output mechanism. As detailed in Section [6,](#page-6-0) the algorithm maintains the state using a two-pointer approach. Token nodes may persist in the state even after they cease to belong to P, because they lie in the window. Therefore, the space complexity relates to the maximum number of nodes simultaneously maintained by the two-pointer algorithm. While a theoretically safe upper bound is O(min(n, mt)), empirical evaluations show that the practical memory footprint is much smaller.

<span id="page-29-0"></span>Table [7](#page-29-0) demonstrates the maximum number of nodes in the window maintained by the two-pointer algorithm with the datasets described in Table [2.](#page-22-0)

*Table 7.* Maximum size in the window during the two-pointer algorithm of eager output.

| Tokenizer | English | Chinese | Code |
|-----------|---------|---------|------|
| P50K      | 26      | 35      | 96   |
| R50K      | 21      | 34      | 96   |
| CL100K    | 32      | 129     | 212  |
| O200K     | 31      | 129     | 208  |

### J.4. End-to-End Benchmarks

We evaluated the end-to-end tokenization speeds for rust-gems and ours. The tokenizer model P50K failed to run with rust-gems; thus, it was excluded from the benchmarks.

The median CPU times (in seconds) across standard datasets are presented in Table [8.](#page-30-0) The results are also demonstrated as a violin plot in Figure [8.](#page-30-1) The baseline implementation is the original BPE implementation in tiktoken. Our incremental approach consistently matches or outperforms the backtracking and table-based implementations.

<span id="page-30-0"></span>*Table 8.* End-to-end CPU time (seconds, median) compared with other incremental BPE implementations. Lower is better.

<span id="page-30-1"></span>![](_page_30_Figure_3.jpeg)

| Model       | Method       | English | Chinese | Code  |
|-------------|--------------|---------|---------|-------|
| Baseline    |              | 0.932   | 1.244   | 1.501 |
| Ours R50K   | (inc)        | 0.925   | 0.897   | 1.369 |
| Ours        | (eager)      | 0.989   | 1.117   | 1.510 |
| via         | backtracking | 0.948   | 1.180   | 1.431 |
| via         | table        | 1.004   | 1.243   | 1.566 |
| Baseline    |              | 1.068   | 1.374   | 1.535 |
| Ours        | (inc)        | 1.064   | 0.815   | 1.422 |
| Ours CL100K | (eager)      | 1.135   | 1.050   | 1.515 |
| via         | backtracking | 1.090   | 1.048   | 1.441 |
| via         | table        | 1.140   | 1.254   | 1.579 |
| Baseline    |              | 1.768   | 1.729   | 2.082 |
| Ours O200K  | (inc)        | 1.739   | 1.047   | 2.032 |
| Ours        | (eager)      | 1.818   | 1.308   | 2.081 |
| via         | backtracking | 1.782   | 1.275   | 2.087 |
| via         | table        | 1.839   | 1.732   | 2.121 |

*Figure 8.* Distributions of end-to-end execution times for different BPE implementations. The violin plots illustrate the latency (in seconds, lower is better) across three tokenizers (R50K, CL100K, O200K) and three datasets (English, Chinese, Code). All methods were evaluated by replacing the core BPE in the tiktoken library. Specifically, baseline refers to the original BPE implementation of tiktoken, while backtracking and table correspond to the encode via backtracking and encode via table methods from rust-gems, respectively. Colored dashed vertical lines indicate the mean execution times for the baseline, ours (inc), and backtracking implementations.