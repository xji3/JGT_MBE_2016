from DirGeneconv import *

#TODO: Expected Num Geneconv etc

class gBGCDirGeneconv(DirGeneconv):
    # add gamma parameter which is equivalent to B in Lartillot's 2013 MBE paper (Phylogenetic Patterns of GC-Biased Gene Conversion...)
    # gamma parameter isn't log-transformed in self.x but used itself
    def get_initial_x_process(self):
        self.gamma = 1.0
        count = np.array([0, 0, 0, 0], dtype = float) # count for A, C, G, T in all seq
        for name in self.name_to_seq:
            for i in range(4):
                count[i] += ''.join(self.name_to_seq[name]).count('ACGT'[i])
        count = count / count.sum()

        if self.Model == 'MG94':
            # x_process[] = %AG, %A, %C, kappa, omega, tau
            self.x_process = np.log(np.array([count[0] + count[2], count[0] / (count[0] + count[2]), count[1] / (count[1] + count[3]),
                                  self.kappa, self.omega]))
            self.x_process = np.concatenate((self.x_process, np.log(self.tau), [self.gamma]))
        elif self.Model == 'HKY':
            # x_process[] = %AG, %A, %C, kappa, tau
            self.omega = 1.0
            self.x_process = np.log(np.array([count[0] + count[2], count[0] / (count[0] + count[2]), count[1] / (count[1] + count[3]),
                                  self.kappa]))
            self.x_process = np.concatenate((self.x_process, np.log(self.tau), [self.gamma]))

        self.x_rates = np.log(0.01 * np.array([ self.edge_to_blen[edge] for edge in self.edge_to_blen.keys()]))
        self.x = np.concatenate((self.x_process, self.x_rates))


        if self.clock:   # set-up x_clock if it's a clock model
            l = len(self.edge_to_blen) / 2 + 1               # number of leaves
            self.x_Lr = np.log(np.ones((l)) * 0.9)
            self.x_clock = np.concatenate((self.x_process, self.x_Lr))
            self.unpack_x_clock()

        self.update_by_x()

    def unpack_x_process(self, Force_process = None):
        self.gamma = self.x_process[-1]
        x_process = np.exp(self.x_process[:-1])

        if Force_process != None:
            for i in Force_process.keys():
                if i == len(x_process):
                    self.gamma = Force_process[i]
                else:
                    x_process[i] = Force_process[i]

        if self.Model == 'MG94':
            # x_process[] = %AG, %A, %C, kappa, omega, tau
            assert(len(self.x_process) == 8)
            
            pi_a = x_process[0] * x_process[1]
            pi_c = (1 - x_process[0]) * x_process[2]
            pi_g = x_process[0] * (1 - x_process[1])
            pi_t = (1 - x_process[0]) * (1 - x_process[2])
            self.pi = [pi_a, pi_c, pi_g, pi_t]
            self.kappa = x_process[3]
            self.omega = x_process[4]
            self.tau = x_process[5:7]
            
        elif self.Model == 'HKY':
            # x_process[] = %AG, %A, %C, kappa, tau
            assert(len(self.x_process) == 7)
            pi_a = x_process[0] * x_process[1]
            pi_c = (1 - x_process[0]) * x_process[2]
            pi_g = x_process[0] * (1 - x_process[1])
            pi_t = (1 - x_process[0]) * (1 - x_process[2])
            self.pi = [pi_a, pi_c, pi_g, pi_t]
            self.kappa = x_process[3]
            self.tau = x_process[4:6]

        # Now update the prior distribution
        self.get_prior()

        # Now update processes (Rate matrices)
        self.get_processes()   

    def get_GC_fitness(self, ca, cb):
        assert(len(ca) == len(cb)) # length should be the same
        # ca got copied by cb. 
        k = cb.count('G') + cb.count('C') - ca.count('G') - ca.count('C')
        if self.gamma == 0.0:
            return 1.0
        else:
            if k == 0:
                return 1.0
            else:
                return (k * self.gamma) / (1 - np.exp(- k * self.gamma))
        
    def get_MG94Geneconv_and_MG94(self):
        Qbasic = self.get_MG94Basic()
        row = []
        col = []
        rate_geneconv = []
        rate_basic = []

        for i, pair in enumerate(product(self.codon_nonstop, repeat = 2)):
            # use ca, cb, cc to denote codon_a, codon_b, codon_c, where cc != ca, cc != cb
            ca, cb = pair
            sa = self.codon_to_state[ca]
            sb = self.codon_to_state[cb]
            if ca != cb:
                for cc in self.codon_nonstop:
                    if cc == ca or cc == cb:
                        continue
                    sc = self.codon_to_state[cc]
                    # (ca, cb) to (ca, cc)
                    Qb = Qbasic[sb, sc]
                    if Qb != 0:
                        row.append((sa, sb))
                        col.append((sa, sc))
                        rate_geneconv.append(Qb)
                        rate_basic.append(0.0)

                    # (ca, cb) to (cc, cb)
                    Qb = Qbasic[sa, sc]
                    if Qb != 0:
                        row.append((sa, sb))
                        col.append((sc, sb))
                        rate_geneconv.append(Qb)
                        rate_basic.append(0.0)

                        
                # (ca, cb) to (ca, ca)
                row.append((sa, sb))
                col.append((sa, sa))
                Qb = Qbasic[sb, sa]
                if isNonsynonymous(cb, ca, self.codon_table):
                    Tgeneconv12 = self.tau[0] * self.omega
                    Tgeneconv21 = self.tau[1] * self.omega
                else:
                    Tgeneconv12 = self.tau[0]
                    Tgeneconv21 = self.tau[1]
                rate_geneconv.append(Qb + Tgeneconv12 * self.get_GC_fitness(cb, ca))
                rate_basic.append(0.0)
                
                # (ca, cb) to (cb, cb)
                row.append((sa, sb))
                col.append((sb, sb))
                Qb = Qbasic[sa, sb]
                rate_geneconv.append(Qb + Tgeneconv21 * self.get_GC_fitness(ca, cb))
                rate_basic.append(0.0)

            else:
                for cc in self.codon_nonstop:
                    if cc == ca:
                        continue
                    sc = self.codon_to_state[cc]

                    # (ca, ca) to (ca,  cc)
                    Qb = Qbasic[sa, sc]
                    if Qb != 0:
                        row.append((sa, sb))
                        col.append((sa, sc))
                        rate_geneconv.append(Qb)
                        rate_basic.append(0.0)
                    # (ca, ca) to (cc, ca)
                        row.append((sa, sb))
                        col.append((sc, sa))
                        rate_geneconv.append(Qb)
                        rate_basic.append(0.0)

                    # (ca, ca) to (cc, cc)
                        row.append((sa, sb))
                        col.append((sc, sc))
                        rate_geneconv.append(0.0)
                        rate_basic.append(Qb)
                
        process_geneconv = dict(
            row = row,
            col = col,
            rate = rate_geneconv
            )
        process_basic = dict(
            row = row,
            col = col,
            rate = rate_basic
            )
        return [process_basic, process_geneconv]

    def get_HKYGeneconv(self):
        #print 'tau = ', self.tau
        Qbasic = self.get_HKYBasic()
        row = []
        col = []
        rate_geneconv = []
        rate_basic = []

        for i, pair_from in enumerate(product('ACGT', repeat = 2)):
            na, nb = pair_from
            sa = self.nt_to_state[na]
            sb = self.nt_to_state[nb]
            for j, pair_to in enumerate(product('ACGT', repeat = 2)):
                nc, nd = pair_to
                sc = self.nt_to_state[nc]
                sd = self.nt_to_state[nd]
                if i == j:
                    continue

                if (na != nc and nb!= nd) or (na == nc and nb == nd):
                    GeneconvRate = 0.0
                if na ==nc and nb != nd:
                    Qb = Qbasic['ACGT'.index(nb), 'ACGT'.index(nd)]
                    if na == nd:
                        GeneconvRate = Qb + self.tau[0] * self.get_GC_fitness(nb, na)
                    else:
                        GeneconvRate = Qb
                if nb == nd and na != nc:
                    Qb = Qbasic['ACGT'.index(na), 'ACGT'.index(nc)]
                    if nb == nc:
                        GeneconvRate = Qb + self.tau[1] * self.get_GC_fitness(na, nb)
                    else:
                        GeneconvRate = Qb

                if GeneconvRate != 0.0:
                    row.append((sa, sb))
                    col.append((sc, sd))
                    rate_geneconv.append(GeneconvRate)
                    rate_basic.append(0.0)
                if na == nb and nc == nd:
                    row.append((sa, sb))
                    col.append((sc, sd))
                    rate_geneconv.append(GeneconvRate)
                    rate_basic.append(Qbasic['ACGT'.index(na), 'ACGT'.index(nc)])

        process_geneconv = dict(
            row = row,
            col = col,
            rate = rate_geneconv
            )
        process_basic = dict(
            row = row,
            col = col,
            rate = rate_basic
            )
        return [process_basic, process_geneconv]

    def save_to_file(self, file_name = None, path = './'):
        if file_name == None:
            file_name = 'gBGC_Dir_' + self.Model + '_' + '_'.join(self.paralog)
            if self.clock:
                file_name += '_clock.p'
            else:
                file_name += '_nonclock.p'
        save_file = path + file_name
        self.ll = self._loglikelihood()[0]
        print 'x = ', self.x, 'x_clock = ', self.x_clock
        save_info = dict(
            Model = self.Model,
            x     = self.x,
            x_clock = self.x_clock,
            edge_to_blen = self.edge_to_blen,
            edge_list = self.edge_list,
            ExpectedGeneconv = self.ExpectedGeneconv,
            ExpectedDwellTime = self.ExpectedDwellTime,
            ll    = self.ll,
            newicktree = self.newicktree,
            alignment_file = self.seqloc,
            paralog = self.paralog,
            clock = self.clock,
            Force = self.Force
            )
        pickle.dump(save_info, open(save_file, 'wb+'))  # use pickle to save the class which can be easily reconstructed by pickle.load()

    def get_directionalNumGeneconvRed(self):
        row12_states = []
        column12_states = []
        proportions12 = []
        
        row21_states = []
        column21_states = []
        proportions21 = []
        if self.Model == 'MG94':
            Qbasic = self.get_MG94Basic()
            for i, pair in enumerate(product(self.codon_nonstop, repeat = 2)):
                ca, cb = pair
                sa = self.codon_to_state[ca]
                sb = self.codon_to_state[cb]
                if ca == cb:
                    continue
                
                # (ca, cb) to (ca, ca)
                row12_states.append((sa, sb))
                column12_states.append((sa, sa))
                Qb = Qbasic[sb, sa]
                if isNonsynonymous(cb, ca, self.codon_table):
                    Tgeneconv12 = self.tau[0] * self.omega
                    Tgeneconv21 = self.tau[1] * self.omega
                else:
                    Tgeneconv12 = self.tau[0]
                    Tgeneconv21 = self.tau[1]
                Tgeneconv = Tgeneconv12 * self.get_GC_fitness(cb, ca)
                proportions12.append(Tgeneconv / (Qb + Tgeneconv) if (Qb + Tgeneconv) >0 else 0.0)

                # (ca, cb) to (cb, cb)
                row21_states.append((sa, sb))
                column21_states.append((sb, sb))
                Qb = Qbasic[sa, sb]
                Tgeneconv = Tgeneconv12 * self.get_GC_fitness(ca, cb)
                proportions21.append(Tgeneconv / (Qb + Tgeneconv) if (Qb + Tgeneconv) >0 else 0.0)
            
        elif self.Model == 'HKY':
            Qbasic = self.get_HKYBasic()
            for i, pair in enumerate(product('ACGT', repeat = 2)):
                na, nb = pair
                sa = self.nt_to_state[na]
                sb = self.nt_to_state[nb]
                if na == nb:
                    continue

                # (na, nb) to (na, na)
                row12_states.append((sa, sb))
                column12_states.append((sa, sa))
                GeneconvRate = get_HKYGeneconvRate(pair, na + na, Qbasic, self.tau[0])
                Tgeneconv = self.tau[0] * self.get_GC_fitness(nb, na)
                proportions12.append(Tgeneconv / (GeneconvRate - self.tau[0] + Tgeneconv) if GeneconvRate > 0 else 0.0)
                

                # (na, nb) to (nb, nb)
                row21_states.append((sa, sb))
                column21_states.append((sb, sb))
                GeneconvRate = get_HKYGeneconvRate(pair, nb + nb, Qbasic, self.tau[1])
                Tgeneconv = self.tau[1] * self.get_GC_fitness(nb, na)
                proportions21.append(Tgeneconv / (GeneconvRate - self.tau[1] + Tgeneconv) if GeneconvRate > 0 else 0.0)
                
        return [{'row_states' : row12_states, 'column_states' : column12_states, 'weights' : proportions12},
                {'row_states' : row21_states, 'column_states' : column21_states, 'weights' : proportions21}]
        


def main(args):
    paralog = [args.paralog1, args.paralog2]
    alignment_file = '../MafftAlignment/' + '_'.join(paralog) + '/' + '_'.join(paralog) + '_input.fasta'
    newicktree = '../PairsAlignemt/YeastTree.newick'
    path = './NewPackageNewRun/'
    omega_guess = 0.1

    print 'Now calculate MLE for pair', paralog

    Force = None
    Force_hky = None

    test_hky = gBGCDirGeneconv( newicktree, alignment_file, paralog, Model = 'HKY', Force = Force_hky, clock = False)
    result_hky = test_hky.get_mle(display = False)
    test_hky.save_to_file(path = path)

    test2_hky = gBGCDirGeneconv( newicktree, alignment_file, paralog, Model = 'HKY', Force = Force_hky, clock = True)
    result2_hky = test2_hky.get_mle(display = False)
    test2_hky.save_to_file(path = path)

    test = gBGCDirGeneconv( newicktree, alignment_file, paralog, Model = 'MG94', Force = Force, clock = False)
    x = np.concatenate((test_hky.x_process[:-3], np.log([omega_guess]), test_hky.x_process[-3:], test_hky.x_rates))
    test.update_by_x(x)
    
    result = test.get_mle(display = True)
    test.save_to_file(path = path)

    test2 = gBGCDirGeneconv( newicktree, alignment_file, paralog, Model = 'MG94', Force = Force, clock = True)
    x_clock = np.concatenate((test2_hky.x_process[:-3], np.log([omega_guess]), test2_hky.x_process[-3:], test2_hky.x_Lr))
    test2.update_by_x_clock(x_clock)
    result = test2.get_mle(display = True)
    test2.save_to_file(path = path)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--paralog1', required = True, help = 'Name of the 1st paralog')
    parser.add_argument('--paralog2', required = True, help = 'Name of the 2nd paralog')
    
    main(parser.parse_args())


##    paralog1 = 'YER131W'
##    paralog2 = 'YGL189C'
##
##    paralog = [paralog1, paralog2]
##    alignment_file = '../MafftAlignment/' + '_'.join(paralog) + '/' + '_'.join(paralog) + '_input.fasta'
##    newicktree = '../PairsAlignemt/YeastTree.newick'
##    Force    = {5:0.0, 6:0.0}
##    Force = None
##    
##    test = gBGCDirGeneconv( newicktree, alignment_file, paralog, Model = 'HKY', Force = Force, clock = False)
##    test.get_mle()
##    test2 = DirGeneconv( newicktree, alignment_file, paralog, Model = 'HKY', Force = Force, clock = False)