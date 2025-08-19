from maad import sound, util, features
from maui import visualizations, acoustic_indices, io, eda, utils
import numpy as np

class AcousticIndices(object):
    """docstring for AcousticIndices"""
    def __init__(self):
        self.available_indices =  {
            "ACI": "ACI",
            "Spectral Events": "spectral_events",
            "Spectral Activity": "spectral_activity",
            "Temporal Entropy": "temporal_entropy",
            "Frequency Entropy": "frequency_entropy",
        }
        self.indices = None
        self.acoustic_indices_methods = []

    def set_indices(self, indices: list):
        self.indices = indices
        self.acoustic_indices_methods = []
        for idx in indices:
            if idx == "ACI": self.acoustic_indices_methods.append(self.get_aci)
            if idx == "spectral_events": self.acoustic_indices_methods.append(self.get_spectral_events)
            if idx == "spectral_activity": self.acoustic_indices_methods.append(self.get_spectral_activity)
            if idx == "temporal_entropy": self.acoustic_indices_methods.append(self.get_temporal_entropy)
            if idx == "frequency_entropy": self.acoustic_indices_methods.append(self.get_frequency_entropy)

    def pre_calculation_method(self, s, fs):
        pre_calc_vars = {"s": s, "fs": fs}
        # ----------------------- ACI -----------------------
        if "ACI" in self.indices:
            Sxx, tn, fn, ext = sound.spectrogram(
                s, fs,
                window='hann', nperseg=1024, noverlap=512,
                mode='amplitude'
            )
            Sxx_pcen, enhance_profile, PCENxx = sound.pcen(
                Sxx,
                gain=0.8, bias=2, power=0.5,
                b=0.025, eps=1e-6
            )
            Sxx_nb, noise_profile, BGNxx = sound.remove_background(
                Sxx_pcen,
                gauss_win=50, gauss_std=25,
                beta1=1, beta2=1, llambda=1
            )
            Sxx_eq = sound.median_equalizer(Sxx_nb)
            pre_calc_vars["Sxx"] = Sxx
            pre_calc_vars["Sxx_eq"] = Sxx_eq
            pre_calc_vars["tn"] = tn
            pre_calc_vars["fn"] = fn
            pre_calc_vars["ext"] = ext
        # ----------------- Spectral Events -----------------
        if (
            "spectral_events" in self.indices or
            "frequency_entropy" in self.indices or
            "spectral_activity" in self.indices
        ):
            Sxx_power, tn_power, fn_power, ext_power = sound.spectrogram(s, fs)
            Sxx_dB = util.power2dB(Sxx_power)
            Sxx_dB_noNoise,_ = sound.remove_background_along_axis(Sxx_dB, mode='ale')   
            Sxx_power_noNoise = util.dB2power(Sxx_dB_noNoise)
            pre_calc_vars["Sxx_power"] = Sxx_power
            pre_calc_vars["tn_power"] = tn_power
            pre_calc_vars["fn_power"] = fn_power
            pre_calc_vars["ext_power"] = ext_power
            pre_calc_vars["Sxx_dB"] = Sxx_dB
            pre_calc_vars["Sxx_dB_noNoise"] = Sxx_dB_noNoise
            pre_calc_vars["Sxx_power_noNoise"] = Sxx_power_noNoise
        return pre_calc_vars

    def to_serializable(self, obj):
        """
        Converte numpy arrays e scalars para listas e tipos nativos Python.
        """
        if isinstance(obj, np.ndarray):
            return [self.to_serializable(x) for x in obj]
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.integer, np.int32, np.int64, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, list):
            return [self.to_serializable(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: self.to_serializable(v) for k, v in obj.items()}
        else:
            return obj

    def get_aci(self, pre_calc_vars):
        aci_xx, aci_per_bin, aci_sum  = features.acoustic_complexity_index(pre_calc_vars['Sxx_eq'])
        raw_indices = {'aci_xx': aci_xx, 'aci_per_bin': aci_per_bin, 'aci_sum': aci_sum}
        indices = {k: self.to_serializable(v) for k, v in raw_indices.items()}
        return indices

    def get_spectral_events(self, pre_calc_vars):
        EVNspFract_per_bin, EVNspMean_per_bin, EVNspCount_per_bin, EVNsp = features.spectral_events(
                    pre_calc_vars['Sxx_dB_noNoise'],
                    dt=pre_calc_vars['tn_power'][1] - pre_calc_vars['tn_power'][0],
                    dB_threshold=6,
                    rejectDuration=0.1,
                    display=False,
                    extent=pre_calc_vars['ext_power'])
        raw_indices = {'EVNspFract_per_bin': EVNspFract_per_bin, 'EVNspMean_per_bin': EVNspMean_per_bin, 'EVNspCount_per_bin': EVNspCount_per_bin, 'EVNsp': EVNsp}
        indices = {k: self.to_serializable(v) for k, v in raw_indices.items()}
        return indices

    def get_frequency_entropy(self, pre_calc_vars):
        Hf, Ht_per_bin = features.frequency_entropy(pre_calc_vars['Sxx_power_noNoise'])
        raw_indices = {'Hf': Hf, 'Ht_per_bin': Ht_per_bin}
        indices = {k: self.to_serializable(v) for k, v in raw_indices.items()}
        return indices

    def get_temporal_entropy(self, pre_calc_vars):
        Ht = features.temporal_entropy(pre_calc_vars['s'])
        raw_indices = {'Ht': Ht}
        indices = {k: self.to_serializable(v) for k, v in raw_indices.items()}
        return indices

    def get_spectral_activity(self, pre_calc_vars):
        LFC, MFC, HFC = features.spectral_cover(pre_calc_vars['Sxx_dB_noNoise'], pre_calc_vars['fn_power'])
        raw_indices = {'LFC': LFC, 'MFC': MFC, 'HFC': HFC}
        indices = {k: self.to_serializable(v) for k, v in raw_indices.items()}
        return indices
