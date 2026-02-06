#!/usr/bin/env python3
import os
import sys
import fnmatch
import json
import ROOT

def fill_tgraph(name, data):
    ret = ROOT.TH1F(name, name, len(data), 0, len(data))
    for idx, (x, y) in enumerate(data):
        ret.SetBinContent(idx+1, y)
        ret.SetBinError(idx+1, 0)
    return ret

if __name__ == '__main__':
    ROOT.gROOT.SetBatch()

    # Handle command line argument
    if len(sys.argv) < 2:
        print("Usage: python3 hltRate_new.py <output_suffix>")
        sys.exit(1)
    
    outputFileName = f'{os.path.splitext(os.path.basename(__file__))[0]}_{sys.argv[1]}'

    preliminary = True

    data = {
        2012: {'Prompt': 420.0, 'Parking': 400.0, 'Scouting': 996.0, 'Fill': 2998, 'Lumi': 0.50},
        2015: {'Prompt': 992.5, 'Parking': 98.8, 'Scouting': 1057.1, 'Fill': 4452, 'Lumi': 0.25},
        2016: {'Prompt': 1005.8, 'Parking': 514.5, 'Scouting': 4467.8, 'Fill': 5418, 'Lumi': 0.91},
        2017: {'Prompt': 976.0, 'Parking': 409.7, 'Scouting': 4635.0, 'Fill': 6324, 'Lumi': 1.01},
        2018: {'Prompt': 1046.4, 'Parking': 2918.7, 'Scouting': 4855.6, 'Fill': 7124, 'Lumi': 1.18},
        2022: {'Prompt': 1776.7, 'Parking': 2438.3, 'Scouting': 22296.7, 'Fill': 8489, 'Lumi': 1.45},
        2023: {'Prompt': 1683.8, 'Parking': 2660.2, 'Scouting': 17114.2, 'Fill': 9044, 'Lumi': 1.66},
        2024: {'Prompt': 2350.8, 'Parking': 4768.19, 'Scouting': 26530.02, 'Fill': 10116, 'Lumi': 1.87},
        2025: {'Prompt': 2894.48, 'Parking': 7647.65, 'Scouting': 37723.05, 'Fill': 10690, 'Lumi': 2.04},
    }

    years = sorted(data.keys())

    prompt_factor = 1000.
    parking_factor = 1000.

    prompt_ymax = 30
    scouting_factor = prompt_factor * 1.
    scouting_ymax = prompt_ymax * scouting_factor / prompt_factor

    v_prompt = []
    v_parking = []
    v_promptPlusParking = []
    v_scouting = []
    v_lumi = []
    for idx, year in enumerate(years):
        label = "2025*" if year == 2025 else str(year)
        v_prompt += [[idx+0.5, data[year]['Prompt'] / prompt_factor]]
        v_parking += [[idx+0.5, data[year]['Parking'] / parking_factor]]
        v_scouting += [[idx+0.5, data[year]['Scouting'] / scouting_factor]]
        v_promptPlusParking += [[idx+0.5, v_prompt[-1][1] + v_parking[-1][1]]]
        v_lumi += [[idx+0.5, data[year]['Lumi']]]

    color_prompt = ROOT.TColor.GetColor('#525CEB')
    color_parking = ROOT.TColor.GetColor('#BFCFE7')
    color_scouting = ROOT.TColor.GetColor('#FFB534')
    color_lumi = ROOT.TColor.GetColor('#FF00FF')

    g_prompt = fill_tgraph('prompt', v_prompt)
    g_prompt.SetLineColor(color_prompt)
    g_prompt.SetFillColor(color_prompt)

    g_parking = fill_tgraph('parking', v_parking)
    g_parking.SetLineColor(color_parking)
    g_parking.SetFillColor(color_parking)

    g_scouting = fill_tgraph('scouting', v_scouting)
    g_scouting.SetLineColor(color_scouting)
    g_scouting.SetFillColor(color_scouting)

    g_promptPlusParking = fill_tgraph('promptPlusParking', v_promptPlusParking)
    g_promptPlusParking.SetLineColor(color_parking)
    g_promptPlusParking.SetFillColor(color_parking)

    g_lumi = fill_tgraph('lumi', v_lumi)
    g_lumi.SetLineColor(0)
    g_lumi.SetFillColor(color_lumi)
    g_lumi.SetFillStyle(3353)
    ROOT.gStyle.SetHatchesSpacing(0.6)
    ROOT.gStyle.SetHatchesLineWidth(2)

    # Apply special style to 2025 bins (last bin)
    last_bin = len(years)
    g_prompt_2025 = g_prompt.Clone("prompt_2025")
    g_prompt_2025.Reset()  # Clear all bins
    ROOT.gStyle.SetHatchesSpacing(0.1)  # Reset to 2025 hatch spacing
    ROOT.gStyle.SetHatchesLineWidth(2)  # Reset to 2025 hatch line width
    g_prompt_2025.SetBinContent(last_bin, g_prompt.GetBinContent(last_bin))  # Set only 2025
    g_prompt_2025.SetBarWidth(0.4)  # Match other years' width
    g_prompt_2025.SetBarOffset(0.3)  # Match other years' width
    g_prompt_2025.SetLineColor(color_prompt)
    g_prompt_2025.SetFillColor(color_prompt)
    g_prompt_2025.SetFillStyle(3353)  # Hatched for 2025
    
    g_promptPlusParking_2025 = g_promptPlusParking.Clone("promptPlusParking_2025")
    g_promptPlusParking_2025.Reset()
    g_promptPlusParking_2025.SetBinContent(last_bin, g_promptPlusParking.GetBinContent(last_bin))
    g_promptPlusParking_2025.SetBarWidth(0.4)  # Match other years' width
    g_promptPlusParking_2025.SetBarOffset(0.3)  # Match other years' width
    g_promptPlusParking_2025.SetLineColor(color_parking)
    g_promptPlusParking_2025.SetFillColor(color_parking)
    g_promptPlusParking_2025.SetFillStyle(3353)   
    g_scouting_2025 = g_scouting.Clone("scouting_2025")
    g_scouting_2025.Reset()
    g_scouting_2025.SetBinContent(last_bin, g_scouting.GetBinContent(last_bin))
    g_scouting_2025.SetBarWidth(0.4)  # Match other years' width                                                                   
    g_scouting_2025.SetBarOffset(0.3)  # Match other years' width
    g_scouting_2025.SetLineColor(color_scouting)
    g_scouting_2025.SetFillColor(color_scouting)
    g_scouting_2025.SetFillStyle(3353)

    # Ensure original histograms exclude 2025 data
    g_prompt.SetBinContent(last_bin, 0)
    g_promptPlusParking.SetBinContent(last_bin, 0)
    g_scouting.SetBinContent(last_bin, 0)

    # ROOT.gStyle.SetHatchesSpacing(0.1)
    # ROOT.gStyle.SetHatchesLineWidth(2)

    g_prompt.SetBarWidth(0.4)
    g_prompt.SetBarOffset(0.3)

    g_promptPlusParking.SetBarWidth(0.4)
    g_promptPlusParking.SetBarOffset(0.3)

    g_scouting.SetBarWidth(0.4)
    g_scouting.SetBarOffset(0.3)

    g_lumi.SetBarWidth(0.4)
    g_lumi.SetBarOffset(0.3)

    canvas_name = 'rate_plot'
    canvas = ROOT.TCanvas(canvas_name, canvas_name, 1200, 1000)
    canvas.cd()

    TOP = 0.06
    BOT = 0.12
    LEF = 0.09
    RIG = 0.02

    v_margin = 0.011

    pad_height = (1 - TOP - BOT - 4 * v_margin) / 3

    canvas.SetTopMargin(TOP)
    canvas.SetBottomMargin(BOT)
    canvas.SetLeftMargin(LEF)
    canvas.SetRightMargin(RIG)

    p0_ymin = 0
    p0_ymax = p0_ymin + BOT + pad_height*1 + v_margin
    p0_factor_y = 1 / (p0_ymax - p0_ymin)
    p0 = ROOT.TPad("p1", "p1", 0, p0_ymin, 1, p0_ymax, 0, 0, 0)
    p0.SetBottomMargin(BOT * p0_factor_y)
    p0.SetTopMargin(v_margin * p0_factor_y)
    p0.SetLeftMargin(LEF)
    p0.SetRightMargin(RIG)
    p0.SetGrid(1,0)
    p0.Draw()
    p0.cd()

    h0 = ROOT.TH1D('h0', '', len(years), 0, len(years))
    h0.SetStats(0)
    h0.Draw()

    canvas.cd()

    p1_ymin = p0_ymax
    p1_ymax = p1_ymin + v_margin + pad_height + v_margin
    p1_factor_y = 1 / (p1_ymax - p1_ymin)
    p1 = ROOT.TPad("p1", "p1", 0, p1_ymin, 1, p1_ymax, 0, 0, 0)
    p1.SetBottomMargin(v_margin * p1_factor_y)
    p1.SetTopMargin(v_margin * p1_factor_y)
    p1.SetLeftMargin(LEF)
    p1.SetRightMargin(RIG)
    p1.SetGrid(1,0)
    p1.Draw()
    p1.cd()

    h1 = ROOT.TH1D('h1', '', len(years), 0, len(years))
    h1.SetStats(0)
    h1.Draw()

    canvas.cd()

    p2_ymin = p1_ymax
    p2_ymax = p2_ymin + v_margin + pad_height + TOP
    p2_factor_y = 1 / (p2_ymax - p2_ymin)
    p2 = ROOT.TPad("p2", "p2", 0, p2_ymin, 1, p2_ymax, 0, 0, 0)
    p2.SetBottomMargin(v_margin * p2_factor_y)
    p2.SetTopMargin(TOP * p2_factor_y)
    p2.SetLeftMargin(LEF)
    p2.SetRightMargin(RIG)
    p2.SetGrid(1,0)
    p2.Draw()
    p2.cd()

    h2 = ROOT.TH1D('h2', '', len(years), 0, len(years))
    h2.SetStats(0)
    h2.Draw()

    nDivs = 506
    for idx, year in enumerate(years):
        label = "2025*" if year == 2025 else str(year)
        h0.GetXaxis().SetBinLabel(idx+1, label)
        h1.GetXaxis().SetBinLabel(idx+1, label)
        h2.GetXaxis().SetBinLabel(idx+1, label)

    h0.GetXaxis().SetTitleSize(0.05)
    h0.GetXaxis().SetTitleOffset(1.0)
    h0.GetXaxis().SetLabelSize(0.05 * 2.5)
    h0.GetXaxis().SetLabelOffset(h0.GetXaxis().GetLabelOffset() * 4)
    h0.GetXaxis().SetLabelFont(62)

    h1.GetXaxis().SetTitleSize(0)
    h1.GetXaxis().SetLabelSize(0)
    h2.GetXaxis().SetTitleSize(0)
    h2.GetXaxis().SetLabelSize(0)

    h0.GetYaxis().SetTitle('Luminosity [10^{34} cm^{-2} s^{-1}]')
    h0.GetYaxis().SetLabelSize(p0_factor_y * 0.03)
    h0.GetYaxis().SetTitleSize(p0_factor_y * 0.0275)
    h0.GetYaxis().SetTitleOffset(0.585)
    h0.GetYaxis().SetRangeUser(0.0001, 2.2)
    h0.GetYaxis().SetNdivisions(nDivs)

    h1.GetYaxis().SetTitle('HLT Rate [kHz]')
    h1.GetYaxis().SetLabelSize(p1_factor_y * 0.03)
    h1.GetYaxis().SetTitleSize(p1_factor_y * 0.0275)
    h1.GetYaxis().SetTitleOffset(0.406)
    h1.GetYaxis().SetRangeUser(0.0001, 11)
    h1.GetYaxis().SetNdivisions(nDivs)

    h2.GetYaxis().SetTitle('HLT Rate [kHz]')
    h2.GetYaxis().SetLabelSize(p2_factor_y * 0.03)
    h2.GetYaxis().SetTitleSize(p2_factor_y * 0.0275)
    h2.GetYaxis().SetTitleOffset(0.475)
    h2.GetYaxis().SetRangeUser(0.0001, 40)
    h2.GetYaxis().SetNdivisions(nDivs)

    p2.cd()

    if preliminary:
        txt0 = ROOT.TPaveText(0.09, 0.86, 0.165, 0.97, 'NDC')
        txt0.SetTextSize(0.125)
    else:
        txt0 = ROOT.TPaveText(0.09, 0.86, 0.18, 0.97, 'NDC')
        txt0.SetTextSize(0.145)
    txt0.SetBorderSize(0)
    txt0.SetFillColor(0)
    txt0.SetFillStyle(1001)
    txt0.SetTextAlign(12)
    txt0.SetTextFont(62)
    txt0.SetTextSize(0.125)
    txt0.SetTextColor(1)
    txt0.AddText('CMS')
    txt0.Draw('same')

    txt00 = ROOT.TPaveText(0.165, 0.85, 0.30, 0.95, 'NDC')
    txt00.SetBorderSize(0)
    txt00.SetFillColor(0)
    txt00.SetFillStyle(1001)
    txt00.SetTextAlign(12)
    txt00.SetTextFont(52)
    txt00.SetTextSize(0.085)
    txt00.SetTextColor(1)
    txt00.AddText('Preliminary')
    if preliminary:
        txt00.Draw('same')
        
    # Draw asterisk note at canvas level
    canvas.cd()
    asterisk_note = ROOT.TPaveText(0.84, 0.005, 0.99, 0.03, "NDC")
    asterisk_note.SetTextSize(0.025)
    asterisk_note.SetBorderSize(0)
    asterisk_note.SetFillColor(0)
    asterisk_note.SetFillStyle(1001)
    asterisk_note.SetTextAlign(12)
    asterisk_note.SetTextFont(42)
    asterisk_note.AddText("* early 2025")
    asterisk_note.Draw("same")

    # if preliminary:
    #     txt00.Draw('same')

    p0.cd()
    tmp = []
    for idx, year in enumerate(years):
        fill_label = f'[Fill {data[year]["Fill"]}]'
        bin_width = (1 - LEF - RIG) / len(years)
        center_x = LEF + bin_width * (idx + 0.5) + 0.01
        
        box_width = 0.12
        txt1 = ROOT.TPaveText(center_x - box_width/2, 0.09, 
                             center_x + box_width/2, 0.15, 'NDC')
        txt1.SetBorderSize(0)
        txt1.SetFillColor(0)
        txt1.SetFillStyle(1001)
        txt1.SetTextAlign(11)
        txt1.SetTextFont(62)
        txt1.SetTextSize(0.06)
        txt1.SetTextColor(ROOT.kGray+1)
        txt1.AddText(fill_label)
        txt1.Draw('same')
        tmp += [txt1]

        lumi_label = 'L_{inst} = ' + f'{data[year]["Lumi"]:3.2f}' + ' cm^{-2} s^{-1}'
        lumi_label_xmin = LEF + (1-LEF-RIG)/len(years) * (idx + 0.14)
        txt2 = ROOT.TPaveText(lumi_label_xmin, 0.83, lumi_label_xmin+0.08, 0.87, 'NDC')
        txt2.SetBorderSize(0)
        txt2.SetFillColor(0)
        txt2.SetFillStyle(1001)
        txt2.SetTextAlign(22)
        txt2.SetTextFont(62)
        txt2.SetTextSize(0.0175)
        txt2.SetTextColor(ROOT.kGray+2)
        txt2.AddText(lumi_label)
        tmp += [txt2]

    p2.cd()
    if preliminary:
        txt3 = ROOT.TPaveText(0.30, 0.84, 0.98, 0.96, 'NDC')
        txt3.SetTextAlign(22)
        txt3.SetTextSize(0.072)
        txt3.AddText('HLT rates and inst. luminosity averaged over one fill of a given data-taking year')
    else:
        txt3 = ROOT.TPaveText(0.20, 0.84, 0.95, 0.96, 'NDC')
        txt3.SetTextAlign(12)
        txt3.SetTextSize(0.075)
        txt3.AddText('HLT rates and instantaneous luminosity averaged over one fill of a given data-taking year')
    txt3.SetBorderSize(0)
    txt3.SetFillColor(0)
    txt3.SetFillStyle(1001)
    txt3.SetTextFont(42)
    txt3.SetTextColor(1)
    txt3.Draw('same')

    p1.cd()
    g_promptPlusParking.Draw('same,bar0')
    g_prompt.Draw('same,bar0')
    g_promptPlusParking_2025.Draw('same,bar0')
    g_prompt_2025.Draw('same,bar0')

    p2.cd()
    g_scouting.Draw('same,bar0')
    g_scouting_2025.Draw('same,bar0')

    p0.cd()
    ROOT.gStyle.SetHatchesSpacing(0.45)
    ROOT.gStyle.SetHatchesLineWidth(2)
    g_lumi.Draw('same,bar0')

    p0.cd()
    h0.Draw('axis,same')
    p1.cd()
    h1.Draw('axis,same')
    p2.cd()
    h2.Draw('axis,same')

    p0.cd()
    leg0 = ROOT.TLegend(0.23, 0.78, 0.48, 0.92)
    leg0.SetBorderSize(2)
    leg0.SetTextFont(42)
    leg0.SetTextSize(p0_factor_y * 0.03)
    leg0.SetFillColor(0)
    leg0.AddEntry(g_lumi, 'Instantaneous Luminosity', 'f')
    leg0.Draw('same')

    p1.cd()
    leg1 = ROOT.TLegend(0.23, 0.55, 0.47, 0.88)
    leg1.SetBorderSize(2)
    leg1.SetTextFont(42)
    leg1.SetTextSize(p1_factor_y * 0.03)
    leg1.SetFillColor(0)
    leg1.AddEntry(g_prompt, 'Standard', 'f')
    leg1.AddEntry(g_promptPlusParking, 'Parking', 'f')
    leg1.Draw('same')

    p2.cd()
    leg2 = ROOT.TLegend(0.23, 0.60, 0.47, 0.75)
    leg2.SetBorderSize(2)
    leg2.SetTextFont(42)
    leg2.SetTextSize(p2_factor_y * 0.03)
    leg2.SetFillColor(0)
    leg2.AddEntry(g_scouting, 'Scouting', 'f')
    leg2.Draw('same')

    canvas.SaveAs(f'{outputFileName}.png')
    canvas.SaveAs(f'{outputFileName}.pdf')
