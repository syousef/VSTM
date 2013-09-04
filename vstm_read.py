import numpy as np


def get_dprime(ans):
    from scipy import stats
    #HR = hit rate, FAR = false alarm rate
    num_hits= np.double(len(ans[ans==1]))
    num_misses= np.double(len(ans[ans==2]))
    num_FA= np.double(len(ans[ans==3]))
    num_CR= np.double(len(ans[ans==4]))
    HR= num_hits/(num_hits+num_misses)
    FAR= num_FA/(num_FA+num_CR)
    if HR==1:
        HR=.999
    if FAR == 0:
        FAR = 0.001
    dprime = stats.norm.ppf(HR) - stats.norm.ppf(FAR)
    if dprime==np.float("inf"):
        print "infinite dprime with HR:",HR, " , FAR:",FAR
    return dprime

def compare_bools(array1,array2):
    if len(array1)==len(array2):
        output=[array1[i] and array2[i] for i in range (len(array1))]
    else: 
        print "array size doesn't match"
        output= -1
    return np.array(output)

def get_kmax(ssize):
    return np.min(ssize)+1

def all_dprimes(ans,ssize,soa):
    kmax=get_kmax(ssize)
    dprimes=[]
    soas=[.025,.2,.025,.2,.025,.2,.025,.2]
    ssizes=[kmax-1,kmax-1,kmax,kmax,kmax+1,kmax+1,kmax+2,kmax+2]
    
    for ss,encoding in zip(ssizes,soas):
        array1 = (ssize==ss)
        array2 = (soa==encoding)
        ans1=ans[compare_bools(array1,array2)]
        dp=get_dprime(ans1)
        dprimes.append(dp)
    return np.array(dprimes),soas,ssizes

def get_files():
    from glob import glob
    fnames=glob("data/*/*/capacity_tstim_*00.0.txt")
    return fnames

def read_file(fname):
    ssize, soa, ans = np.genfromtxt(fname, unpack=True, usecols=(1,2,6), skip_header=11)
    return ssize, soa, ans

def do_ttest(s1, s2):
    from scipy.stats import ttest_ind
    #if we want Welche's t-test (population variences not equal) set equal_var=False
    t,p = ttest_ind(s1,s2,equal_var=True)
    return t,p

def do_anova(arrays):
    from scipy.stats import f_oneway
    #should be a list of lists, i.e. arrays = [[1,2,3],[1,2,3],...,[1,2,3]]
    F,p = f_oneway(*arrays)
    return F,p

def plot_drugplacebo(drug, drugerr, placebo, placeboerr,ti="Drug vs. Placebo",figname=""):
    from pylab import clf,bar,ylabel,xlabel,legend,title,savefig,show
    
    #prepare for plotting
    index=np.arange(len(drug))
    width=.3
    clf()

    #plot it up
    bar(index, drug,width,color='r',yerr=drugerr,error_kw=dict(elinewidth=2, ecolor='black'))
    bar(index+width,placebo,width,color='b',yerr=placeboerr,error_kw=dict(elinewidth=2, ecolor='black'))

    #add labels
    ylabel("Performance (dprime)")
    xlabel("Set Size")
    title(ti)
    legend(["Drug","Placebo"],loc=0)

    #output
    if figname=="":
        show()
    else:
        savefig(figname)
    
def write_excel(colnames,data, sheetname="dprime", filename="vstm_data_analysis.xls"):
    import xlwt as xl
    bk = xl.Workbook()
    sh = bk.add_sheet(sheetname)
    #add headers
    for i in range(len(colnames)):
        sh.write(0,i,colnames[i])
    
    for rownum, rowcontent in enumerate(data):
        for i in range(len(rowcontent)):
            sh.write(rownum+1,i,rowcontent[i])
    
    bk.save(filename)

def translate(k, ss, tstim, soa):
    if ss == k-1:
        ss2 = "A"
    elif ss == k:
        ss2 = "B"
    elif ss == k+1:
        ss2 = "C"
    elif ss == k+2:
        ss2 = "D"

    if tstim == "100":
        tstim2 = "short"
    elif tstim == "200":
        tstim2 = "long"

    if soa == .025:
        soa2 = "short"
    elif soa == .200:
        soa2 = "long"

    return ss2, tstim2, soa2

if __name__=="__main__":
    output=open('vstm_data_analysis_dprime.txt',"w")
    fnames=get_files()
    data = []
    for subj_file in fnames:
        #extract info from file name
        junk,subjname,dayname,filename=subj_file.split("/")
        drug=dayname[-1]
        tstim=filename[15:18]
        #import data
        ssize,soa,ans = read_file(subj_file)
        #calculate dprime
        dprimes,soas,ssizes = all_dprimes(ans,ssize,soa)
        kmax = get_kmax(ssizes)
        
        if (dayname=="day2_P" or dayname=="day3_D"):
            order = "PF"
        elif (dayname=="day3_P" or dayname=="day2_D"):
            order = "DF"
        for i in range(len(soas)):
            ssize_str, tstim_str, soa_str = translate(kmax,ssizes[i],tstim,soas[i])
            data.append([subjname, order, drug, ssize_str,tstim_str,soa_str, dprimes[i]])

    colnames = ["SUBJ","ORDER","PILL","SS","TSTIM","ENCODING","DPRIME"]        
    write_excel(colnames,data, sheetname="dprime", filename="vstm_anova.xls")
#        dprimes2 = dprimes*1.2
        
#        dpserr = .5
#        dps2err = .1

#        plot_drugplacebo(dprimes,dpserr,dprimes2,dps2err)
#        break
    
