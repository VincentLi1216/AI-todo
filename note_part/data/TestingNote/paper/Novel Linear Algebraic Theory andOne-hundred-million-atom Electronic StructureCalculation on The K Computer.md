#### **1. Introduction**

- **Objective**: Develop and implement a novel linear algebraic algorithm, the multiple Arnoldi (mArnoldi) method, to calculate electronic structures for systems with over 100 million atoms.
- **Significance**:
    - Breakthrough in large-scale electronic structure calculations, achieving order-N computational cost.
    - Demonstrated capability on the K computer with silicon crystals and nano-composite materials.
    - Applications in modeling materials at unprecedented scales.

---

#### **2. Methodology**

1. **mArnoldi Method**:
    
    - Solves generalized shifted linear equations: (zS−H)x=b(zS - H)x = b where HH is the Hamiltonian, SS is the overlap matrix, and xx is the solution vector.
    - Reduces the original eigenvalue problem to small subspace eigenvalue calculations within Krylov subspaces.
2. **Algorithm Features**:
    
    - High parallel efficiency leveraging sparse matrix properties.
    - Utilizes ν×ν\nu \times \nu subspaces (ν=30−300\nu = 30-300) to solve problems iteratively.
    - Efficient computation of Green’s functions for total energy and force calculations.
3. **Parallel Efficiency**:
    
    - Measured on the K computer using up to 663,552 cores.
    - Achieved strong scaling with efficiency rates:
        - 98% at 98,304 cores.
        - 90% at 294,912 cores.
        - 73% at maximum cores.

---

#### **3. Results**

1. **Large-Scale Calculations**:
    
    - Successfully simulated systems with 100 million atoms (e.g., silicon crystals and nano-composite carbon solids).
    - Demonstrated linear scaling of computational cost relative to the number of atoms.
2. **Eigenvalue Calculations**:
    
    - Applied to calculate specific eigenstates for a polymer system, poly-(9,9 dioctyl-fluorene).
    - Confirmed results via agreement with ab initio calculations for smaller systems.
3. **Wavefunction Analysis**:
    
    - Calculated highest-occupied (HO) and lowest-unoccupied (LU) molecular orbitals.
    - Identified localization patterns of wavefunctions in amorphous-like polymer structures.

---

#### **4. Applications**

1. **Material Science**:
    - Modeling electronic structures of large-scale materials, such as semiconductors and polymers.
    - Analysis of nano-composite and amorphous materials.
2. **Molecular Dynamics**:
    - Combined with molecular dynamics simulations to study non-ideal polymer structures and thermal relaxation.
3. **Multidisciplinary Impact**:
    - Potential for interdisciplinary applications between physics, mathematics, and material science.

---

#### **5. Challenges and Future Directions**

1. **Model Parameter Automation**:
    - Development of methods for automatic determination of tight-binding parameters to enhance usability.
2. **Matrix Libraries**:
    - Expansion of ELSES matrix data for broader applicability in computational research.
3. **Algorithm Refinement**:
    - Exploration of advanced eigenvalue solvers (e.g., Jacobi-Davidson methods) for improved accuracy and efficiency.

---

#### **6. Conclusion**

- **Innovation**:
    - The mArnoldi method represents a major advancement in linear algebra and material simulation.
    - Demonstrates unprecedented scalability and efficiency for electronic structure calculations.
- **Outlook**:
    - Promises to revolutionize computational material science and enable discoveries at nanoscale and beyond.