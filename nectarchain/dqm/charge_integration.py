
from dqm_summary_processor import *

class ChargeIntegration_HighLowGain(dqm_summary):

    def __init__(self, gaink):

    	self.k = gaink
    	return None

    def ConfigureForRun(self,path, Chan, Samp):
        #define number of channels and samples
        self.Chan = Chan
        self.Samp= Samp

        self.counter_evt = 0
        self.counter_ped = 0

        self.camera = CameraGeometry.from_name("NectarCam-003")
        self.cmap = 'gnuplot2'

        reader1=EventSource(input_url=path, max_events = 1)
        self.subarray = reader1.subarray
        subarray = reader1.subarray
        subarray.tel[0].camera.readout = ctapipe.instrument.camera.readout.CameraReadout.from_name("NectarCam")
        config = Config({"LocalPeakWindowSum": {"window_shift": 12, "window_width": 12}})

        self.integrator = LocalPeakWindowSum(subarray, config=config)

        self.image_all = []
        self.peakpos_all =  []

        self.image_ped = []
        self.peakpos_ped = []


    def ProcessEvent(self, evt):
        waveform=evt.r1.tel[0].waveform[self.k]
        image, peakpos = self.integrator(waveform,0,np.zeros(self.Chan, dtype = int))

        if evt.trigger.event_type == 32: #count peds 
            self.counter_ped += 1
            self.image_ped.append(image)
            self.peakpos_ped.append(peakpos)
        else:
            self.counter_evt += 1
            self.image_all.append(image)
            self.peakpos_all.append(peakpos)
    	

    def FinishRun(self):

        self.peakpos_all = np.array(self.peakpos_all, dtype = float) 
        if self.counter_ped > 0:
            self.peakpos_ped = np.array(self.peakpos_ped, dtype = float)

        #rms, percentile, mean deviation, median, mean, 
        self.image_all = np.array(self.image_all, dtype = float)       
        self.image_all_median = np.median(self.image_all, axis=0)
        self.image_all_average = np.mean(self.image_all, axis=0)
        self.image_all_std = np.std(self.image_all, axis=0)
        self.image_all_rms = np.sqrt(np.sum(self.image_all**2, axis=0))

        if self.counter_ped > 0:
            self.image_ped = np.array(self.image_ped, dtype = float)
            self.image_ped_median = np.median(self.image_ped, axis=0)
            self.image_ped_average = np.mean(self.image_ped, axis=0)
            self.image_ped_std = np.std(self.image_ped, axis=0)
            self.image_ped_rms = np.sqrt(np.sum(self.image_ped**2, axis=0))


    
    def GetResults(self):

        self.ChargeInt_Results_Dict = {}

        if (self.k==0):
            self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-IMAGE-ALL-AVERAGE-HIGH-GAIN"]  = self.image_all_average
            self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-IMAGE-ALL-MEDIAN-HIGH-GAIN"]  = self.image_all_median
            self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-IMAGE-ALL-RMS-HIGH-GAIN"]  = self.image_all_rms
            self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-IMAGE-ALL-STD-HIGH-GAIN"]  = self.image_all_std

            if self.counter_ped > 0:
                self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-PED-ALL-AVERAGE-HIGH-GAIN"]  = self.image_ped_average
                self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-PED-ALL-MEDIAN-HIGH-GAIN"]  = self.image_ped_median
                self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-PED-ALL-RMS-HIGH-GAIN"]  = self.image_ped_rms
                self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-PED-ALL-STD-HIGH-GAIN"]  = self.image_ped_std

        if (self.k ==1):
            self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-IMAGE-ALL-AVERAGE-LOW-GAIN"]  = self.image_all_average 
            self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-IMAGE-ALL-MEDIAN-LOW-GAIN"]  = self.image_all_median
            self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-IMAGE-ALL-RMS-LOW-GAIN"]  = self.image_all_rms
            self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-IMAGE-ALL-STD-LOW-GAIN"]  = self.image_all_std
            
            if self.counter_ped > 0:
                self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-PED-ALL-AVERAGE-LOW-GAIN"]  = self.image_ped_average
                self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-PED-ALL-MEDIAN-LOW-GAIN"]  = self.image_ped_median
                self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-PED-ALL-RMS-LOW-GAIN"]  = self.image_ped_rms
                self.ChargeInt_Results_Dict["CHARGE-INTEGRATION-PED-ALL-STD-LOW-GAIN"]  = self.image_ped_std
        

        return self.ChargeInt_Results_Dict


    def PlotResults(self,name,FigPath):
        self.ChargeInt_Figures_Dict = {}
        self.ChargeInt_Figures_Names_Dict = {}


        titles = ['All', 'Pedestals']
        if (self.k==0):
            gain_c = 'High'
        if (self.k ==1):
            gain_c = 'Low'

        #Charge integration MEAN plot
        fig1, disp = plt.subplots()
        disp = CameraDisplay(self.subarray.tels[0].camera)
        disp.image = self.image_all_average
        disp.cmap = plt.cm.coolwarm
        disp.axes.text(2, -0.8, f'{gain_c} gain integrated charge (DC)', fontsize=12,rotation=90)
        disp.add_colorbar()

        plt.title("Charge Integration Mean %s Gain (ALL)" %gain_c)

        full_name = name + '_ChargeInt_Mean_%sGain_All.png' %gain_c 
        FullPath = FigPath +full_name
        self.ChargeInt_Figures_Dict["CHARGE-INTEGRATION-IMAGE-ALL-AVERAGE-%s-GAIN" %gain_c] = fig1
        self.ChargeInt_Figures_Names_Dict["CHARGE-INTEGRATION-IMAGE-ALL-AVERAGE-%s-GAIN" %gain_c] = FullPath

        plt.close()


        if self.counter_ped > 0:
            fig2, disp = plt.subplots()
            disp = CameraDisplay(self.subarray.tels[0].camera)
            disp.image = self.image_ped_average
            disp.cmap = plt.cm.coolwarm
            disp.axes.text(2, -0.8, f'{gain_c} gain integrated charge (DC)', fontsize=12,rotation=90)
            disp.add_colorbar()

            plt.title("Charge Integration Mean %s Gain (PED)" %gain_c)

            full_name = name + '_ChargeInt_Mean_%sGain_Ped.png' %gain_c 
            FullPath = FigPath +full_name
            self.ChargeInt_Figures_Dict["CHARGE-INTEGRATION-IMAGE-PED-AVERAGE-%s-GAIN" %gain_c] = fig2
            self.ChargeInt_Figures_Names_Dict["CHARGE-INTEGRATION-IMAGE-PED-AVERAGE-%s-GAIN" %gain_c] = FullPath

            plt.close()


        #Charge integration MEDIAN plot
        fig3, disp = plt.subplots()
        disp = CameraDisplay(self.subarray.tels[0].camera)
        disp.image = self.image_all_median
        disp.cmap = plt.cm.coolwarm
        disp.axes.text(2, -0.8, f'{gain_c} gain integrated charge (DC)', fontsize=12,rotation=90)
        disp.add_colorbar()

        plt.title("Charge Integration Median %s Gain (ALL)" %gain_c)

        full_name = name + '_ChargeInt_Median_%sGain_All.png' %gain_c 
        FullPath = FigPath +full_name
        self.ChargeInt_Figures_Dict["CHARGE-INTEGRATION-IMAGE-ALL-MEDIAN-%s-GAIN" %gain_c] = fig3
        self.ChargeInt_Figures_Names_Dict["CHARGE-INTEGRATION-IMAGE-ALL-MEDIAN-%s-GAIN" %gain_c] = FullPath

        plt.close()


        if self.counter_ped > 0:
            fig4, disp = plt.subplots()
            disp = CameraDisplay(self.subarray.tels[0].camera)
            disp.image = self.image_ped_median
            disp.cmap = plt.cm.coolwarm
            disp.axes.text(2, -0.8, f'{gain_c} gain integrated charge (DC)', fontsize=12,rotation=90)
            disp.add_colorbar()

            plt.title("Charge Integration Median %s Gain (PED)" %gain_c)
            
            full_name = name + '_ChargeInt_Median_%sGain_Ped.png' %gain_c
            FullPath = FigPath +full_name
            self.ChargeInt_Figures_Dict["CHARGE-INTEGRATION-IMAGE-PED-MEDIAN-%s-GAIN" %gain_c] = fig4
            self.ChargeInt_Figures_Names_Dict["CHARGE-INTEGRATION-IMAGE-PED-MEDIAN-%s-GAIN" %gain_c] = FullPath

            plt.close()


        #Charge integration STD plot
        fig5, disp = plt.subplots()
        disp = CameraDisplay(self.subarray.tels[0].camera)
        disp.image = self.image_all_std
        disp.cmap = plt.cm.coolwarm
        disp.axes.text(2, -0.8, f'{gain_c} gain integrated charge (DC)', fontsize=12,rotation=90)
        disp.add_colorbar()

        plt.title("Charge Integration STD %s Gain (ALL)" %gain_c)
            
        full_name = name + '_ChargeInt_Std_%sGain_All.png' %gain_c
        FullPath = FigPath +full_name
        self.ChargeInt_Figures_Dict["CHARGE-INTEGRATION-IMAGE-ALL-STD-%s-GAIN" %gain_c] = fig5
        self.ChargeInt_Figures_Names_Dict["CHARGE-INTEGRATION-IMAGE-ALL-STD-%s-GAIN" %gain_c] = FullPath

        plt.close()
        
        if self.counter_ped > 0:
            fig6, disp = plt.subplots()
            disp = CameraDisplay(self.subarray.tels[0].camera)
            disp.image = self.image_ped_std
            disp.cmap = plt.cm.coolwarm
            disp.axes.text(2, -0.8, f'{gain_c} gain integrated charge (DC)', fontsize=12,rotation=90)
            disp.add_colorbar()

            plt.title("Charge Integration STD %s Gain (PED)" %gain_c)
            
            full_name = name + '_ChargeInt_Std_%sGain_Ped.png' %gain_c
            FullPath = FigPath +full_name
            self.ChargeInt_Figures_Dict["CHARGE-INTEGRATION-IMAGE-PED-STD-%s-GAIN" %gain_c] = fig6
            self.ChargeInt_Figures_Names_Dict["CHARGE-INTEGRATION-IMAGE-PED-STD-%s-GAIN" %gain_c] = FullPath

            plt.close()


        
        #Charge integration RMS plot
        fig7, disp = plt.subplots()
        disp = CameraDisplay(self.subarray.tels[0].camera)
        disp.image = self.image_all_rms
        disp.cmap = plt.cm.coolwarm
        disp.axes.text(2, -0.8, f'{gain_c} gain integrated charge (DC)', fontsize=12,rotation=90)
        disp.add_colorbar()

        plt.title("Charge Integration RMS %s Gain (ALL)" %gain_c)
            
        full_name = name + '_ChargeInt_Rms_%sGain_All.png' %gain_c
        FullPath = FigPath +full_name
        self.ChargeInt_Figures_Dict["CHARGE-INTEGRATION-IMAGE-ALL-RMS-%s-GAIN" %gain_c] = fig7
        self.ChargeInt_Figures_Names_Dict["CHARGE-INTEGRATION-IMAGE-ALL-RMS-%s-GAIN" %gain_c] = FullPath

        plt.close()

        if self.counter_ped > 0:
            fig8, disp = plt.subplots()
            disp = CameraDisplay(self.subarray.tels[0].camera)
            disp.image = self.image_ped_rms
            disp.cmap = plt.cm.coolwarm
            disp.axes.text(2, -0.8, f'{gain_c} gain integrated charge (DC)', fontsize=12,rotation=90)
            disp.add_colorbar()

            plt.title("Charge Integration RMS %s Gain (PED)" %gain_c)
            
            full_name = name + '_ChargeInt_Rms_%sGain_Ped.png' %gain_c
            FullPath = FigPath +full_name
            self.ChargeInt_Figures_Dict["CHARGE-INTEGRATION-IMAGE-PED-RMS-%s-GAIN" %gain_c] = fig8
            self.ChargeInt_Figures_Names_Dict["CHARGE-INTEGRATION-IMAGE-PED-RMS-%s-GAIN" %gain_c] = FullPath

            plt.close()


        #Charge integration SPECTRUM
        fig9, disp = plt.subplots()
        for i in range(self.Chan):
            plt.hist(self.image_all[:,i],100, fill=False, density = True, stacked=True, linewidth=1, log = True, alpha = 0.01)
        plt.hist(np.mean(self.image_all, axis=1),100, color = 'r', linewidth=1, log = True, alpha = 1, label = 'Camera average')
        plt.legend()
        plt.xlabel("Charge (DC)")
        plt.title("Charge spectrum %s gain (ALL)" %gain_c)
            
        full_name = name + '_Charge_Spectrum_%sGain_All.png' %gain_c 
        FullPath = FigPath +full_name
        self.ChargeInt_Figures_Dict["CHARGE-INTEGRATION-SPECTRUM-ALL-%s-GAIN" %gain_c] = fig9
        self.ChargeInt_Figures_Names_Dict["CHARGE-INTEGRATION-SPECTRUM-ALL-%s-GAIN" %gain_c] = FullPath

        plt.close()

        if self.counter_ped > 0:
            fig10, disp = plt.subplots()
            for i in range(self.Chan):
                plt.hist(self.image_ped[:,i],100, fill=False, density = True, stacked=True, linewidth=1, log = True, alpha = 0.01)
            plt.hist(np.mean(self.image_ped, axis=1),100, color = 'r', linewidth=1, log = True, alpha = 1, label = 'Camera average')
            plt.legend()
            plt.xlabel("Charge (DC)")
            plt.title("Charge spectrum %s gain (PED)" %gain_c)
                
            full_name = name + '_Charge_Spectrum_%sGain_Ped.png' %gain_c  
            FullPath = FigPath +full_name
            self.ChargeInt_Figures_Dict["CHARGE-INTEGRATION-SPECTRUM-PED-%s-GAIN" %gain_c] = fig10
            self.ChargeInt_Figures_Names_Dict["CHARGE-INTEGRATION-SPECTRUM-PED-%s-GAIN" %gain_c] = FullPath

            plt.close()


        return  self.ChargeInt_Figures_Dict, self.ChargeInt_Figures_Names_Dict



