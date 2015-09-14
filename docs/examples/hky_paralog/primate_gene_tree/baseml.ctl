      seqfile = for.paml.ECP_EDN.fasta
     treefile = for.paml.newick.tree

      outfile = mlb           * main result file name
        noisy = 3  * 0,1,2,3,9: how much rubbish on the screen
      verbose = 0  * 0: concise; 1: detailed, 2: too much
      runmode = 0  * 0: user tree;  1: semi-automatic;  2: automatic

        model = 4   * 0:JC69, 1:K80, 2:F81, 3:F84, 4:HKY85, 5:T92, 6:TN93, 7:REV
                    * 8:UNREST, 9:REVu; 10:UNRESTu
        Mgene = 1   * 0:rates, 1:separate; 2:diff pi, 3:diff kappa, 4:all diff

        clock = 0   * 0:no clock, 1:clock; 2:local clock; 3:CombinedAnalysis
    fix_kappa = 0   * 0: estimate kappa; 1: fix kappa at value below
        kappa = 2.5   * initial or fixed kappa
 
    fix_alpha = 1   * 0: estimate alpha; 1: fix alpha at value below
        alpha = 0.   * initial or fixed alpha, 0:infinity (constant rate)
        ncatG = 5   * # of categories in the dG, AdG, or nparK models of rates
      fix_rho = 1   * 0: estimate rho; 1: fix rho at value below
          rho = 0   * initial or fixed rho, 0:no correlation
        nparK = 0   * rate-class models. 1:rK, 2:rK&fK, 3:rK&MK(1/K), 4:rK&MK 
        nhomo = 1   * 0 & 1: homogeneous, 2: kappa for branches, 3:N1, 4:N2, 5:user
        getSE = 0   * 0: don't want SEs of estimates, 1: want SEs
 RateAncestor = 0   * (0,1,2): rates (alpha>0) or ancestral states
       method = 0   * 0: simultaneous; 1: one branch at a time

   Small_Diff = 1e-6
    cleandata = 0  * remove sites with ambiguity data (1:yes, 0:no)?
*   fix_blength = 1  * 0: ignore, -1: random, 1: initial, 2: fixed
