---
tags:
  - symbolic regression
  - transcendental functions
  - floating-point arithmetic
  - scientific computing
  - numerical optimization
  - high precision computing
  - symbolic spaces
  - algorithm discovery
  - compiler optimization
  - evolutionary algorithm
---
#### **1. Introduction**

- **Objective**: Leverage an evolutionary algorithm, AutoNumerics-Zero, to automatically discover optimized programs for computing transcendental functions with high precision and efficiency.
- **Key Features**:
    - Designed for limited precision settings, such as float32.
    - Surpasses traditional mathematical approximations like Taylor series or Padé approximants.
    - Incorporates symbolic regression at scale to optimize for precision and computational cost.

---

#### **2. Methodology**

1. **Evolutionary Algorithm**:
    
    - **Outer Loop**: Utilizes a distributed variant of NSGA-II (dNSGA-II) for symbolic regression, searching for optimal program structures.
    - **Inner Loop**: Optimizes floating-point coefficients with CMA-ES, an evolutionary strategy.
    - Programs represented as compute graphs, encoding basic operations (+, −, ×, ÷).
2. **Optimization Targets**:
    
    - **Precision**: Measured by maximum relative error or unit-in-the-last-place (ULP) error for floating-point arithmetic.
    - **Speed**: Evaluated on specific hardware and compilers, integrating compiler effects like pipelining and speculative execution.
3. **Key Innovations**:
    
    - Automatic discovery of reusable intermediate results to reduce computation cost.
    - Accounts for practical issues like rounding errors and compiler behavior.

---

#### **3. Results**

1. **Real-Valued Functions**:
    
    - Evolved programs for g(x)=2xg(x) = 2^x achieve orders of magnitude higher precision than baselines for the same operation count.
    - Techniques like Taylor expansions, Padé approximants, and Chebyshev polynomials are outperformed.
2. **Floating-Point Computations**:
    
    - Programs optimized for float32 achieve more than 3x speed improvements over traditional baselines.
    - Discovered representations trigger favorable compiler behaviors, such as optimized single-thread execution.
3. **Generalization to Other Functions**:
    
    - Extensible to logarithms, error functions, and oscillatory functions like the Airy Ai function.
    - Demonstrates compact and accurate approximations even for challenging domains.

---

#### **4. Applications**

- **Scientific Computing**:
    - Optimization of frequently used transcendental functions (e.g., exponentials, logarithms) for specific hardware setups.
    - Cost reduction in simulations and data-intensive tasks.
- **Algorithm Discovery**:
    - Extends to symbolic regression for novel mathematical relationships and physical equations.
- **Industrial Use**:
    - Custom computations for large-scale simulations, e.g., molecular dynamics or finite-element methods.

---

#### **5. Challenges and Future Directions**

1. **Optimization Complexity**:
    
    - Need for scalable methods to explore large symbolic spaces.
    - Difficulty in optimizing beyond float32 or float64 precision due to increased computational demands.
2. **Compiler Dependence**:
    
    - Discovered programs are highly specific to compilers and hardware, requiring reevaluation for new environments.
3. **Automation of Auxiliary Processes**:
    
    - Potential for automating range reduction and incorporating diverse CPU instructions (e.g., bit shifts).
4. **Interdisciplinary Integration**:
    
    - Application of symbolic regression methods to physics, machine learning, and other scientific domains.

---

#### **6. Conclusion**

- **AutoNumerics-Zero** represents a breakthrough in automating the discovery of efficient mathematical programs.
- Demonstrates the synergy of symbolic regression, evolutionary computation, and real-world compiler effects.
- Opens avenues for further exploration in numerical computation, scientific modeling, and algorithmic discovery.