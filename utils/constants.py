from pathlib import Path

# General
sample_rate = 16000
manual_annotation_patterns = ['<+[^<>]*>+', '``/``', "''/''"]

AUDIO_SEGMENT_GAP = 1 # in sec
SPEECH_GAP = 0.25       # in sec (minimum legth of audio to be counted as silence)
ALLOWED_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "abcdefghijklmnopqrstuvwxyz" + "0123456789" + " '.,:;!?-" + "\"$%&*") # "ÄÖÜäöüáéíóúñ" 


# # Home PC 
data_base = Path("D:\\Robin_dataset\\Switchboard Computed")

timing_dir = data_base / "Timings"
disfluencies_dir = data_base / "Disfluencies"
audio_dir = Path("D:\\Robin_dataset\\Switchboard\\LDC97S62 Switchboard-1 Release 2") # data_base / "Speech"

# # Cluster
# data_base = Path("/export/data3/bachelor_theses/ramann/data")

# timing_dir = data_base / "Switchboard-1 Release 2 Transcripts"
# disfluencies_dir = Path("/project/data_asr/LDC/LDC99T42/treebank_3/dysfl/mgd/swbd")
# audio_dir = Path("/project/data_asr/LDC/LDC97S62")


# General
manual_dir = data_base / "Manual"
manual_seg_dir = data_base / "Manual_Segmented"
automatic_seg_dir = data_base /  "Automatic_Segmented_And_Timed" # "Automatic_Segmented"
transcript_align_dir = data_base / "Manual_Automatic_Alignment"
audio_automatic_align_dir = data_base / "Audio_Whisper_Alignment"
hesitation_dir = data_base / "Automatic_Segmented_Retranscribed_ctc"

model_dir = Path('supervised_data_preperation/data/models')
error_dir = Path('supervised_data_preperation/data/errors')
hesitations_file = Path('supervised_data_preperation/data/hesitations/hesitations.txt')


# corrupt, missing files, wrong length, switch timing
ignore_files = ['2006', '2010', '2027', '2064', '2072', '2073', '2110', '2130', '2171', '2177', '2235', '2247', '2262', '2279', '2289', '2290', '2292', '2303', '2305', '2339', '2366', '2372', '2405', '2434', '2476', '2485', '2501', '2514', '2521', '2527', '2533', '2539', '2543', '2566', '2576', '2593', '2616', '2617', '2627', '2631', '2658', '2684', '2707', '2789', '2792', '2794', '2844', '2854', '2858', '2909', '2912', '2913', '2914', '2923', '2926', '2929', '2930', '2931', '2932', '2935', '2937', '2939', '2942', '2945', '2954', '2955', '2957', '2959', '2960', '2961', '2963', '2965', '2968', '2970', '2981', '2983', '2994', '2999', '3000', '3012', '3013', '3018', '3039', '3040', '3050', '3061', '3077', '3088', '3096', '3130', '3131', '3136', '3138', '3140', '3142', '3143', '3144', '3146', '3148', '3154', '3405', '4379']

# contoversial files. both audios etc
c20 = ['sw2092B005', 'sw2020A036', 'sw2092B014', 'sw2005B007', 'sw2079A008', 'sw2060A014', 'sw2092B017', 'sw2078A006', 'sw2085A014', 'sw2062B021', 'sw2025B002', 'sw2053A002', 'sw2035A014', 'sw2079A006', 'sw2086B021', 'sw2086A010', 'sw2078B025', 'sw2018A000', 'sw2020B008', 'sw2078B019', 'sw2065B026', 'sw2062B029', 'sw2065B001', 'sw2086B015', 'sw2062B030', 'sw2032B007', 'sw2005B013', 'sw2005B018', 'sw2078B015', 'sw2008A010', 'sw2020A023', 'sw2053A011', 'sw2090B018', 'sw2005B016', 'sw2025A004', 'sw2078B016', 'sw2092B013', 'sw2078A005', 'sw2092B006', 'sw2019B004', 'sw2090B008', 'sw2051A007', 'sw2092B008', 'sw2086B017', 'sw2005A011', 'sw2039B028', 'sw2032B014', 'sw2005A017', 'sw2095B006', 'sw2020A029', 'sw2005B020', 'sw2093A009', 'sw2020A007', 'sw2065B009', 'sw2078B026', 'sw2062A015', 'sw2051A021', 'sw2041A014', 'sw2039B013', 'sw2078B018', 'sw2025B000', 'sw2085B007', 'sw2005B017', 'sw2025B015', 'sw2060A015', 'sw2039B019', 'sw2035A005', 'sw2090A003', 'sw2032B021', 'sw2092B007', 'sw2092B015', 'sw2090B013', 'sw2020A005', 'sw2019A012', 'sw2065B023', 'sw2035A013', 'sw2005B009', 'sw2092B018', 'sw2025A012', 'sw2005B012', 'sw2065A012', 'sw2060A000', 'sw2090B014', 'sw2092B003', 'sw2078A000', 'sw2051B000']
c21 = ['sw2107A007', 'sw2131A016', 'sw2185B001', 'sw2105B010', 'sw2107A022', 'sw2151B008', 'sw2113B001', 'sw2184B025', 'sw2187B012', 'sw2124B012', 'sw2122B026', 'sw2107A021', 'sw2175B019', 'sw2102A007', 'sw2122B004', 'sw2149B008', 'sw2113B010', 'sw2107A013', 'sw2178A014', 'sw2107B005', 'sw2111B016', 'sw2113A014', 'sw2184A017', 'sw2105B007', 'sw2122B017', 'sw2107B014', 'sw2155B026', 'sw2122B019', 'sw2178B022', 'sw2187B031', 'sw2113B014', 'sw2111B014', 'sw2139A023', 'sw2131A022', 'sw2184B003', 'sw2191A009', 'sw2139A016', 'sw2105A001', 'sw2122B007', 'sw2168A012', 'sw2113A004', 'sw2131A004', 'sw2107B013', 'sw2125B016', 'sw2168B012', 'sw2107B001', 'sw2149B019', 'sw2191A007', 'sw2131B000', 'sw2131A023', 'sw2111A008', 'sw2107B016', 'sw2113A011', 'sw2139A033', 'sw2122B018', 'sw2124B004', 'sw2107A018', 'sw2109B010', 'sw2191B014', 'sw2101B021', 'sw2101A006', 'sw2131A014', 'sw2185B010', 'sw2149B009', 'sw2145A009', 'sw2145A015', 'sw2122B012', 'sw2122B013', 'sw2131A007', 'sw2145A006', 'sw2107A025', 'sw2122B003', 'sw2163B000', 'sw2178A018', 'sw2111B002', 'sw2113B015', 'sw2113B011', 'sw2131B020', 'sw2139A027', 'sw2178B013', 'sw2122B010', 'sw2184B000', 'sw2107B011', 'sw2122B009', 'sw2191B009', 'sw2122B002', 'sw2149B013', 'sw2168A001', 'sw2131A025', 'sw2131A009', 'sw2125B005', 'sw2122B001', 'sw2185A009', 'sw2101B017', 'sw2124B003', 'sw2124B013', 'sw2184B006', 'sw2175B012', 'sw2175B013', 'sw2184A016', 'sw2122B015', 'sw2105B005', 'sw2122B020', 'sw2122B011', 'sw2184B019', 'sw2190A007', 'sw2191A008', 'sw2168A013', 'sw2178A013', 'sw2122B023']
c22 = ['sw2295A006', 'sw2241A028', 'sw2226A004', 'sw2227B008', 'sw2227B016', 'sw2266B005', 'sw2253A009', 'sw2287A011', 'sw2293B000', 'sw2249B020', 'sw2231A009', 'sw2227B001', 'sw2275B016', 'sw2287A010', 'sw2266B006', 'sw2266B013', 'sw2260A012', 'sw2268B019', 'sw2253B018', 'sw2226A002', 'sw2275A010', 'sw2226A016', 'sw2253A031', 'sw2234A009', 'sw2278A019', 'sw2275A023', 'sw2221B022', 'sw2259A013', 'sw2264B011', 'sw2227B013', 'sw2241A006', 'sw2221B021', 'sw2227B004', 'sw2264A007', 'sw2232A021', 'sw2227B006', 'sw2244B006', 'sw2252B009', 'sw2229B005', 'sw2260A004', 'sw2205A012', 'sw2227B009', 'sw2226B020', 'sw2227B000', 'sw2252B012', 'sw2275A006', 'sw2295A016', 'sw2299A015', 'sw2232A022', 'sw2265B007', 'sw2275B024', 'sw2263B014', 'sw2253A016', 'sw2249B008', 'sw2278A026', 'sw2295A005', 'sw2221B019', 'sw2253A005', 'sw2231A023', 'sw2278A022', 'sw2260A003', 'sw2237B015', 'sw2249B014', 'sw2227B010', 'sw2220B019', 'sw2253A019', 'sw2278A034', 'sw2227B014', 'sw2205A009', 'sw2248A007', 'sw2241B028', 'sw2227B002', 'sw2232A010', 'sw2299B011', 'sw2278A024', 'sw2278A014', 'sw2278A030', 'sw2227B018', 'sw2260A020', 'sw2221A015', 'sw2278A021', 'sw2265A011', 'sw2231A008', 'sw2226B017', 'sw2260A006', 'sw2248A009', 'sw2205A024', 'sw2287A000', 'sw2295A011', 'sw2227B017', 'sw2249B017', 'sw2268B003', 'sw2249B028', 'sw2227B005', 'sw2231A002', 'sw2266A007', 'sw2221A026', 'sw2253A002', 'sw2226A010', 'sw2220B006', 'sw2231A019', 'sw2253A027', 'sw2260A024', 'sw2231B014', 'sw2260A008', 'sw2283A016', 'sw2264A003', 'sw2287B000', 'sw2241A007']
c23 = ['sw2368A005', 'sw2382A027', 'sw2325B024', 'sw2370B015', 'sw2344B006', 'sw2362B007', 'sw2355A013', 'sw2355B016', 'sw2382A004', 'sw2309A006', 'sw2370B019', 'sw2309A019', 'sw2354A001', 'sw2382A024', 'sw2344B001', 'sw2340B025', 'sw2354A016', 'sw2365B019', 'sw2382A017', 'sw2376A008', 'sw2354A027', 'sw2355A007', 'sw2324B006', 'sw2355A011', 'sw2355B011', 'sw2331A000', 'sw2368A008', 'sw2300A019', 'sw2330A010', 'sw2334B030', 'sw2314B019', 'sw2376B001', 'sw2331B020', 'sw2368B025', 'sw2368A004', 'sw2387A017', 'sw2331B025', 'sw2349A011', 'sw2342A014', 'sw2395A010', 'sw2370B012', 'sw2349A013', 'sw2349A004', 'sw2300A030', 'sw2355B013', 'sw2365B020', 'sw2368A023', 'sw2382A013', 'sw2362B019', 'sw2340B000', 'sw2301A004', 'sw2325B028', 'sw2354A002', 'sw2395B000', 'sw2362B013', 'sw2387A022', 'sw2376A006', 'sw2344B026', 'sw2325A010', 'sw2387A018', 'sw2365B022', 'sw2340B014', 'sw2300A029', 'sw2353B027', 'sw2399A022', 'sw2349B013', 'sw2386A024', 'sw2370A022', 'sw2355A005', 'sw2383A009', 'sw2368B023', 'sw2325B022', 'sw2368B002', 'sw2344B028', 'sw2365A019', 'sw2340B003', 'sw2355A003', 'sw2368A024', 'sw2383A008', 'sw2349A010', 'sw2340A020', 'sw2387A016', 'sw2302A016', 'sw2334B013', 'sw2355A001', 'sw2325A007', 'sw2309B011', 'sw2382A008', 'sw2331B002', 'sw2393A022', 'sw2368A026', 'sw2325B003', 'sw2397A013', 'sw2397B027', 'sw2331A009', 'sw2353B009', 'sw2399A011', 'sw2370B016', 'sw2300A028', 'sw2340B019', 'sw2395A022', 'sw2376A013', 'sw2370B010', 'sw2331A016', 'sw2300B006', 'sw2325A011', 'sw2325B035', 'sw2300A020', 'sw2349A009', 'sw2376A004', 'sw2365B029', 'sw2370B017', 'sw2387A020', 'sw2376A003', 'sw2399A004', 'sw2365B023', 'sw2399A023', 'sw2362B000', 'sw2380B002', 'sw2376B002', 'sw2309A000', 'sw2353B025', 'sw2387A014', 'sw2370B023', 'sw2355B020', 'sw2368A027', 'sw2300A017', 'sw2368A021', 'sw2340B018', 'sw2362B030', 'sw2336A000', 'sw2314B017', 'sw2354A013', 'sw2386B024', 'sw2353B030', 'sw2386B029']
c24 = ['sw2471B003', 'sw2495B015', 'sw2437B025', 'sw2471B012', 'sw2439B027', 'sw2479A003', 'sw2442A020', 'sw2439B006', 'sw2427A010', 'sw2446B024', 'sw2477A018', 'sw2455B004', 'sw2479B009', 'sw2448B004', 'sw2452A020', 'sw2433B005', 'sw2439B026', 'sw2431A009', 'sw2433B026', 'sw2479A004', 'sw2407A011', 'sw2439B029', 'sw2479A005', 'sw2490A008', 'sw2477A003', 'sw2433B013', 'sw2427A012', 'sw2433A024', 'sw2499B008', 'sw2406B020', 'sw2469A013', 'sw2433B028', 'sw2483A027', 'sw2439B024', 'sw2490A020', 'sw2427A023', 'sw2426A026', 'sw2435B023', 'sw2431A028', 'sw2482B023', 'sw2406B024', 'sw2413A009', 'sw2457B008', 'sw2479A019', 'sw2431B008', 'sw2488B013', 'sw2486B032', 'sw2499B022', 'sw2439A010', 'sw2436A024', 'sw2452B007', 'sw2469A021', 'sw2482B005', 'sw2457A007', 'sw2460B012', 'sw2421A005', 'sw2479A027', 'sw2477B018', 'sw2452B027', 'sw2435A017', 'sw2427B003', 'sw2433A010', 'sw2436B008', 'sw2431B020', 'sw2467A024', 'sw2448B023', 'sw2495B021', 'sw2427B004', 'sw2452B016', 'sw2439B003', 'sw2479A000', 'sw2469A024', 'sw2435B033', 'sw2482B020', 'sw2486B011', 'sw2433B017', 'sw2418B025', 'sw2429B002', 'sw2427B021', 'sw2437B024', 'sw2477A022', 'sw2495A016', 'sw2435B019', 'sw2426A002', 'sw2437B019', 'sw2457B013', 'sw2465B012', 'sw2429B005', 'sw2469A004', 'sw2427A025', 'sw2465B023', 'sw2441B005', 'sw2427A002', 'sw2427A015', 'sw2452B000', 'sw2492B009', 'sw2427A021', 'sw2439A013', 'sw2431B025', 'sw2486B009', 'sw2457A002', 'sw2457B004', 'sw2479B020', 'sw2423B004', 'sw2490A025', 'sw2450B004', 'sw2488B006', 'sw2457A010', 'sw2448B016', 'sw2441B023', 'sw2406A000', 'sw2466A003', 'sw2488B000', 'sw2429B029', 'sw2433B021', 'sw2413A013', 'sw2439A024', 'sw2427A001', 'sw2461A009', 'sw2406B012', 'sw2418B022', 'sw2441B013', 'sw2435B011', 'sw2423B007', 'sw2478A012', 'sw2469A028', 'sw2461A012', 'sw2472B005', 'sw2479A001', 'sw2479B023', 'sw2478B000', 'sw2442A018', 'sw2455B009', 'sw2482B022', 'sw2439A034', 'sw2479A002', 'sw2435B025', 'sw2466A000', 'sw2439A015', 'sw2472B018', 'sw2460A016', 'sw2433B007', 'sw2441B025', 'sw2442B000', 'sw2477A024', 'sw2499B030', 'sw2433B004', 'sw2427B008', 'sw2427A017', 'sw2406B007', 'sw2452B019', 'sw2490A017', 'sw2452A025', 'sw2469A017', 'sw2457B017', 'sw2492A003', 'sw2486B021', 'sw2492A015', 'sw2433B018', 'sw2469B002', 'sw2439A001', 'sw2448B011', 'sw2437A013', 'sw2486B000', 'sw2477B009', 'sw2488B003', 'sw2495B009', 'sw2479B000', 'sw2436A017', 'sw2426A015', 'sw2479B022', 'sw2439B016', 'sw2431A000', 'sw2457A016', 'sw2435B000', 'sw2433B014', 'sw2499A001', 'sw2499B029', 'sw2465B024', 'sw2427A020', 'sw2435A025', 'sw2418B027', 'sw2477A015', 'sw2448B021', 'sw2499B027', 'sw2486B016', 'sw2433B008', 'sw2479B008', 'sw2441B031', 'sw2478B013', 'sw2427A006', 'sw2433B027', 'sw2460B019', 'sw2448B014', 'sw2433B029', 'sw2421A009', 'sw2457B000', 'sw2477B005', 'sw2435B001', 'sw2457B021', 'sw2460A020']
c25 = ['sw2552B000', 'sw2510B011', 'sw2547B003', 'sw2511B021', 'sw2519B014', 'sw2547B005', 'sw2562A023', 'sw2540A009', 'sw2597A018', 'sw2554B027', 'sw2528B000', 'sw2515B015', 'sw2558B005', 'sw2519B005', 'sw2559B014', 'sw2506A026', 'sw2515B022', 'sw2586A008', 'sw2562A001', 'sw2548A000', 'sw2510A020', 'sw2589A017', 'sw2528A023', 'sw2548B005', 'sw2597A000', 'sw2554B021', 'sw2554B010', 'sw2519A001', 'sw2571A020', 'sw2525A015', 'sw2525A008', 'sw2579A004', 'sw2571A029', 'sw2570A022', 'sw2526A024', 'sw2586A010', 'sw2510B017', 'sw2565B007', 'sw2578B024', 'sw2554B007', 'sw2568A019', 'sw2537A003', 'sw2565B017', 'sw2597A026', 'sw2506A021', 'sw2594A005', 'sw2525A038', 'sw2525A020', 'sw2510A018', 'sw2570A009', 'sw2578A023', 'sw2585B018', 'sw2547A026', 'sw2554B030', 'sw2586A015', 'sw2578A008', 'sw2585B004', 'sw2524B000', 'sw2525A035', 'sw2537B012', 'sw2506A003', 'sw2570A020', 'sw2519B002', 'sw2510A024', 'sw2570A011', 'sw2548B016', 'sw2557A013', 'sw2519B003', 'sw2587A004', 'sw2586B007', 'sw2519A007', 'sw2519A008', 'sw2525A029', 'sw2554B029', 'sw2515B034', 'sw2571A008', 'sw2594B015', 'sw2586B009', 'sw2511A004', 'sw2565B009', 'sw2549A018', 'sw2519B004', 'sw2548A009', 'sw2540A015', 'sw2548B007', 'sw2528B014', 'sw2578A024', 'sw2540A010', 'sw2594B013', 'sw2599B007', 'sw2586A014', 'sw2547A030', 'sw2525A011', 'sw2571B003', 'sw2571A017', 'sw2586A011', 'sw2584A027', 'sw2584B015', 'sw2587A026', 'sw2548A007', 'sw2571A010', 'sw2510A027', 'sw2594B024', 'sw2540A003', 'sw2598A017', 'sw2552A028', 'sw2510A000', 'sw2594B027', 'sw2562A000', 'sw2549B023', 'sw2570A010', 'sw2510B025', 'sw2570B016', 'sw2506B011', 'sw2504A022', 'sw2565B002', 'sw2519A000', 'sw2502A027', 'sw2526A027', 'sw2586A009', 'sw2525A031', 'sw2525A023', 'sw2571B014', 'sw2548B000', 'sw2578A026', 'sw2525A036', 'sw2510A022', 'sw2568A025', 'sw2557A012', 'sw2525A018']
c26 = ['sw2667B015', 'sw2669B006', 'sw2648B016', 'sw2610A020', 'sw2648B026', 'sw2667A001', 'sw2640B006', 'sw2672A011', 'sw2693B016', 'sw2650B027', 'sw2602A011', 'sw2604B015', 'sw2647A008', 'sw2650B010', 'sw2648B007', 'sw2615A020', 'sw2679B006', 'sw2647A016', 'sw2652A006', 'sw2610A029', 'sw2676B022', 'sw2692B024', 'sw2608A017', 'sw2657B017', 'sw2672A004', 'sw2679A016', 'sw2692B005', 'sw2663B001', 'sw2647A002', 'sw2692B002', 'sw2657B010', 'sw2653B001', 'sw2647A023', 'sw2642A023', 'sw2615B026', 'sw2628B016', 'sw2648B024', 'sw2692B016', 'sw2692B029', 'sw2621A010', 'sw2672A016', 'sw2650B026', 'sw2630A005', 'sw2610A025', 'sw2614A001', 'sw2667B018', 'sw2647A017', 'sw2603A019', 'sw2672A032', 'sw2640B014', 'sw2630A028', 'sw2642A020', 'sw2652A007', 'sw2609A021', 'sw2667B021', 'sw2642A012', 'sw2661B006', 'sw2672A024', 'sw2657B001', 'sw2645A013', 'sw2662A003', 'sw2610A007', 'sw2648B022', 'sw2679A008', 'sw2630A012', 'sw2679A018', 'sw2648B002', 'sw2679B004', 'sw2610B006', 'sw2663B016', 'sw2692A021', 'sw2640B003', 'sw2621A013', 'sw2620B021', 'sw2692B000', 'sw2630A010', 'sw2615B024', 'sw2645A009', 'sw2672A003', 'sw2622A023', 'sw2645B013', 'sw2647A025', 'sw2638A008', 'sw2621A011', 'sw2692A027', 'sw2640B007', 'sw2620B018', 'sw2611A010', 'sw2692B028', 'sw2638A012', 'sw2630A006', 'sw2667B025', 'sw2608A021', 'sw2667A014', 'sw2692A011', 'sw2662A018', 'sw2610A012', 'sw2669B010', 'sw2652A009', 'sw2653A013', 'sw2623B018', 'sw2650B013', 'sw2630A025', 'sw2638A020', 'sw2638B004', 'sw2603A013', 'sw2676B000', 'sw2692B014', 'sw2652A001', 'sw2648B029', 'sw2628B001', 'sw2645B017', 'sw2648B006', 'sw2653B012', 'sw2667B024', 'sw2667B023', 'sw2638A014', 'sw2640B011', 'sw2638A021', 'sw2640B001']
c27 = ['sw2734B015', 'sw2717B002', 'sw2768A018', 'sw2713B014', 'sw2711B016', 'sw2768A021', 'sw2736B017', 'sw2723B013', 'sw2726A015', 'sw2788A010', 'sw2788A011', 'sw2761B017', 'sw2723B024', 'sw2797B002', 'sw2710B007', 'sw2768A011', 'sw2797B032', 'sw2744A018', 'sw2709B009', 'sw2770A008', 'sw2710A004', 'sw2723B026', 'sw2726A013', 'sw2736B000', 'sw2726A021', 'sw2726A014', 'sw2797B041', 'sw2703A008', 'sw2744B028', 'sw2744A023', 'sw2782B022', 'sw2741A003', 'sw2756A019', 'sw2772A026', 'sw2744A029', 'sw2797B031', 'sw2719B022', 'sw2775A003', 'sw2768B016', 'sw2759A019', 'sw2703B004', 'sw2768B009', 'sw2790B020', 'sw2782B003', 'sw2709B008', 'sw2710A030', 'sw2782B018', 'sw2713A031', 'sw2788B024', 'sw2772A032', 'sw2741B010', 'sw2724A025', 'sw2723B023', 'sw2710A000', 'sw2767B028', 'sw2716A014', 'sw2713B000', 'sw2744A006', 'sw2788B009', 'sw2797B043', 'sw2788A022', 'sw2710A029', 'sw2716A016', 'sw2793B016', 'sw2726B002', 'sw2726A003', 'sw2703B008', 'sw2780B018', 'sw2744B010', 'sw2788A026', 'sw2719B028', 'sw2790A026', 'sw2726A022', 'sw2723B027', 'sw2768A007', 'sw2770B004', 'sw2723B022', 'sw2744A025', 'sw2790A012', 'sw2751A016', 'sw2788A018', 'sw2744A019', 'sw2751A013', 'sw2761B009', 'sw2768A004', 'sw2790A001', 'sw2772A021', 'sw2717B011', 'sw2726B019', 'sw2768A024', 'sw2726A009', 'sw2723B016', 'sw2766B007', 'sw2713B004', 'sw2719B002', 'sw2719B005', 'sw2744A024', 'sw2744A013', 'sw2719B021', 'sw2744A002', 'sw2703B014', 'sw2768A027', 'sw2719B003', 'sw2759A015', 'sw2766B030', 'sw2766B021', 'sw2703B010', 'sw2768A005', 'sw2775A000', 'sw2759A013', 'sw2729B004', 'sw2774B005', 'sw2744B011', 'sw2744B015', 'sw2768B023', 'sw2773B018', 'sw2726A008', 'sw2776B009', 'sw2723B002', 'sw2719B014', 'sw2726A018', 'sw2716A011', 'sw2741B011', 'sw2788A027', 'sw2729B017', 'sw2729B008', 'sw2708A014', 'sw2741A015', 'sw2788A020', 'sw2759A007', 'sw2782B001', 'sw2782B007', 'sw2713B008', 'sw2761B005', 'sw2729B001', 'sw2723B018', 'sw2768B021', 'sw2726B012', 'sw2723B025', 'sw2772A018', 'sw2772A010', 'sw2729A002', 'sw2768A020', 'sw2782B005', 'sw2766B009', 'sw2768A014', 'sw2744B019', 'sw2768B026', 'sw2772B023', 'sw2703B007', 'sw2717B004', 'sw2768B022', 'sw2770B001', 'sw2719B031', 'sw2703B029', 'sw2713B015', 'sw2703B025']
c28 = ['sw2849B006', 'sw2875B024', 'sw2830B014', 'sw2812A025', 'sw2849B017', 'sw2827B000', 'sw2820A009', 'sw2849B012', 'sw2826A014', 'sw2821A003', 'sw2806B005', 'sw2893B008', 'sw2849A010', 'sw2888A006', 'sw2849A015', 'sw2887A014', 'sw2871B031', 'sw2830B002', 'sw2812A008', 'sw2851B015', 'sw2889B012', 'sw2800B020', 'sw2818A006', 'sw2875B012', 'sw2868A004', 'sw2893A014', 'sw2820A013', 'sw2820A012', 'sw2821A008', 'sw2832A021', 'sw2837B015', 'sw2818A011', 'sw2818A019', 'sw2879A019', 'sw2800B009', 'sw2849A004', 'sw2898B008', 'sw2830A019', 'sw2800B012', 'sw2842B006', 'sw2871A024', 'sw2818A000', 'sw2821B016', 'sw2834B013', 'sw2875B021', 'sw2821B002', 'sw2821A017', 'sw2839B028', 'sw2875B023', 'sw2806B011', 'sw2820B010', 'sw2849A017', 'sw2806A025', 'sw2898B007', 'sw2812A015', 'sw2812A019', 'sw2887B012', 'sw2830B028', 'sw2875A009', 'sw2875B020', 'sw2821A001', 'sw2839B009', 'sw2883B009', 'sw2812B024', 'sw2830A026', 'sw2888A005', 'sw2818A028', 'sw2819A014', 'sw2883B001', 'sw2893A018', 'sw2818A004', 'sw2868B025', 'sw2887B014', 'sw2876A003', 'sw2832A010', 'sw2826A021', 'sw2887A004', 'sw2803A030', 'sw2812A002', 'sw2887A019', 'sw2898A025', 'sw2821A027', 'sw2870B006', 'sw2818A003', 'sw2812B020', 'sw2830A013', 'sw2847B005', 'sw2871A020', 'sw2818A015', 'sw2806B022', 'sw2862B002', 'sw2806B014', 'sw2832A002', 'sw2837B010', 'sw2842A000', 'sw2803A023', 'sw2896B002', 'sw2830B021', 'sw2830B000', 'sw2832A028', 'sw2849A001', 'sw2803A010', 'sw2875B018', 'sw2832A008', 'sw2849A007', 'sw2812B000', 'sw2860A025', 'sw2820A006', 'sw2888B000', 'sw2821B020', 'sw2834B006', 'sw2800B005', 'sw2812A012', 'sw2893A005', 'sw2887B025', 'sw2851B011', 'sw2862B019', 'sw2876A012', 'sw2851B004', 'sw2803A013', 'sw2842B009', 'sw2830B011', 'sw2868A000', 'sw2837B008', 'sw2888B019', 'sw2849A023', 'sw2893A020', 'sw2871A005', 'sw2887B020', 'sw2870A025', 'sw2812A024', 'sw2868B022', 'sw2874A020', 'sw2849A018', 'sw2830B022', 'sw2832A023', 'sw2821B013', 'sw2835B015', 'sw2830B016', 'sw2819A009', 'sw2828B006', 'sw2875A006', 'sw2839B011', 'sw2887B019', 'sw2876A008', 'sw2893A016', 'sw2803A017', 'sw2812B014', 'sw2812A021', 'sw2847B015', 'sw2819A001', 'sw2888A012', 'sw2870B019', 'sw2803A018', 'sw2835B029', 'sw2893B012', 'sw2818A023', 'sw2862A010', 'sw2803A032', 'sw2862B006', 'sw2803A022', 'sw2806B001', 'sw2887B030', 'sw2830B004', 'sw2898B023', 'sw2803A027', 'sw2836A020', 'sw2868A007']
c29 = ['sw2924B005', 'sw2984B009', 'sw2956A028', 'sw2934B010', 'sw2934B023', 'sw2993B025', 'sw2969A019', 'sw2938A019', 'sw2900B004', 'sw2910B014', 'sw2900B003', 'sw2996A010', 'sw2952B020', 'sw2924B014', 'sw2927B001', 'sw2952A009', 'sw2992B015', 'sw2967A007', 'sw2944B001', 'sw2953B016', 'sw2962A019', 'sw2915B001', 'sw2952A022', 'sw2944B025', 'sw2924B001', 'sw2969A011', 'sw2967A019', 'sw2927A011', 'sw2992A007', 'sw2953B021', 'sw2921A014', 'sw2995A005', 'sw2944B020', 'sw2993B024', 'sw2967A009', 'sw2927B003', 'sw2917B026', 'sw2993B023', 'sw2927B005', 'sw2992A014', 'sw2967A004', 'sw2984A023', 'sw2993B016', 'sw2956B007', 'sw2953A004', 'sw2915B009', 'sw2938A008', 'sw2953A006', 'sw2967A005', 'sw2953B011', 'sw2952A016', 'sw2969A003', 'sw2952A013', 'sw2995A013', 'sw2915B010', 'sw2900B014', 'sw2956B004', 'sw2992A004', 'sw2952A000', 'sw2953B031', 'sw2915B005', 'sw2969B011', 'sw2956B011', 'sw2995A022', 'sw2953A021', 'sw2984A017', 'sw2956B000', 'sw2944B012', 'sw2927A009', 'sw2921B001', 'sw2996A004', 'sw2934B000']
c30 = ['sw3025A012', 'sw3070A010', 'sw3021B006', 'sw3062A007', 'sw3025B021', 'sw3062B011', 'sw3049B019', 'sw3055A016', 'sw3011A016', 'sw3029A009', 'sw3055A011', 'sw3014A019', 'sw3021B008', 'sw3069A010', 'sw3069A003', 'sw3034A004', 'sw3045A005', 'sw3073A000', 'sw3074A009', 'sw3021B003', 'sw3099B020', 'sw3085A021', 'sw3052B010', 'sw3080A025', 'sw3041B010', 'sw3023B000', 'sw3003A011', 'sw3047B001', 'sw3047B018', 'sw3080A007', 'sw3090B018', 'sw3019A016', 'sw3070A025', 'sw3002B019', 'sw3082B002', 'sw3041A002', 'sw3003A015', 'sw3075A023', 'sw3002B013', 'sw3074B017', 'sw3030A006', 'sw3028B016', 'sw3070A002', 'sw3069B004', 'sw3055A000', 'sw3085A022', 'sw3072B008', 'sw3080A014', 'sw3071B011', 'sw3085A017', 'sw3055A005', 'sw3021B018', 'sw3030A003', 'sw3055A015', 'sw3021B021', 'sw3074B010', 'sw3071B001', 'sw3092A005', 'sw3021B010', 'sw3074A015', 'sw3045B020', 'sw3081A011', 'sw3062A016', 'sw3072A017', 'sw3047B027', 'sw3082B021', 'sw3062B018', 'sw3014A002', 'sw3030A005', 'sw3020B002', 'sw3041A017', 'sw3099B022', 'sw3090A007', 'sw3093A017', 'sw3075B004', 'sw3003A003', 'sw3055A001', 'sw3065A011', 'sw3075B022', 'sw3099B006', 'sw3063A008', 'sw3020B011', 'sw3038B019', 'sw3080A021', 'sw3045A012', 'sw3003B003', 'sw3014A009', 'sw3071B015', 'sw3069A004', 'sw3070A004', 'sw3019A005', 'sw3082B004', 'sw3086B011', 'sw3097A012', 'sw3080A016', 'sw3092A018', 'sw3074B015', 'sw3072B017', 'sw3062A008', 'sw3087B019', 'sw3087B004', 'sw3020B004', 'sw3099B010', 'sw3099B002', 'sw3090B014', 'sw3080A000', 'sw3074A023', 'sw3095A016', 'sw3067A001', 'sw3064B011', 'sw3085A025', 'sw3067A020', 'sw3075A017', 'sw3086B004', 'sw3075A013', 'sw3047B007', 'sw3064A026', 'sw3071B019', 'sw3041A005', 'sw3003B006', 'sw3004B015', 'sw3097A015', 'sw3071B003', 'sw3070A020', 'sw3003B017', 'sw3049B025', 'sw3080A018', 'sw3007A002', 'sw3070A009', 'sw3086B001', 'sw3092A010', 'sw3071B017', 'sw3020B010', 'sw3064B012', 'sw3063B003', 'sw3021B014', 'sw3071B006', 'sw3014A007', 'sw3002B001', 'sw3082B009', 'sw3041A000', 'sw3041B014', 'sw3090A005', 'sw3052B013', 'sw3042B000', 'sw3082B017', 'sw3011A008', 'sw3049A008', 'sw3069B015', 'sw3007A001', 'sw3092A013', 'sw3064A007', 'sw3090A012', 'sw3055A017', 'sw3090B016', 'sw3097A008', 'sw3021B005', 'sw3014A023', 'sw3051A025', 'sw3014A001', 'sw3003A022', 'sw3034A011', 'sw3007A021', 'sw3014A018', 'sw3049B010', 'sw3009B006', 'sw3099B005', 'sw3073B003', 'sw3023B009', 'sw3049B004', 'sw3030A011', 'sw3064B025', 'sw3019A010', 'sw3081A001', 'sw3028B014', 'sw3019A017', 'sw3014A021', 'sw3085A015', 'sw3038B017', 'sw3038B016', 'sw3063A005', 'sw3072A000', 'sw3020B012', 'sw3085A023', 'sw3065B022', 'sw3041B003', 'sw3025B018', 'sw3074A017', 'sw3090A010', 'sw3062B010', 'sw3064B021', 'sw3062A011', 'sw3025B020', 'sw3041A014', 'sw3073B001', 'sw3072B013', 'sw3045A026', 'sw3003A004', 'sw3038A015', 'sw3097A022', 'sw3071B014', 'sw3082B006', 'sw3085A013', 'sw3090B005', 'sw3047B022', 'sw3097A023', 'sw3028A021', 'sw3073A014', 'sw3045A008', 'sw3092A011', 'sw3074A012', 'sw3081B017']
c31 = ['sw3171B010', 'sw3190B000', 'sw3102B017', 'sw3190A011', 'sw3155B005', 'sw3195B017', 'sw3135A002', 'sw3184B006', 'sw3190A007', 'sw3135B001', 'sw3135A013', 'sw3105A018', 'sw3120B007', 'sw3181B003', 'sw3171B009', 'sw3166B015', 'sw3102B005', 'sw3111A026', 'sw3181A017', 'sw3190B006', 'sw3105A021', 'sw3135B022', 'sw3133B000', 'sw3115A007', 'sw3162B012', 'sw3190A003', 'sw3152A007', 'sw3103B014', 'sw3103B012', 'sw3135B025', 'sw3171B006', 'sw3102B023', 'sw3108B010', 'sw3190A000', 'sw3174A013', 'sw3107B009', 'sw3189B003', 'sw3135B027', 'sw3158A009', 'sw3166B010', 'sw3102B016', 'sw3152A009', 'sw3189A008', 'sw3156A010', 'sw3108A010', 'sw3135B020', 'sw3181B014', 'sw3155A005', 'sw3190B004', 'sw3171B002', 'sw3135B016', 'sw3189B018', 'sw3120B000', 'sw3189B017', 'sw3182B008', 'sw3108B015', 'sw3166B003', 'sw3189B001', 'sw3115B000', 'sw3187A011', 'sw3156A009', 'sw3185B000', 'sw3133B013', 'sw3124A013', 'sw3155B002', 'sw3108B007', 'sw3120B014', 'sw3111A002', 'sw3166B012', 'sw3115A002', 'sw3115A024', 'sw3135A020', 'sw3135B023', 'sw3152A004', 'sw3104A014', 'sw3102B008', 'sw3195B005', 'sw3174A009', 'sw3190B011', 'sw3186B012', 'sw3174A002', 'sw3151B003', 'sw3191A011', 'sw3174A012', 'sw3152A017', 'sw3103B029', 'sw3162A010', 'sw3158B007', 'sw3174A007', 'sw3190B007']
c32 = ['sw3232A010', 'sw3227B006', 'sw3227A012', 'sw3228A006', 'sw3257B002', 'sw3245B000', 'sw3216A014', 'sw3280B011', 'sw3284A007', 'sw3237B003', 'sw3238B000', 'sw3223B012', 'sw3239A001', 'sw3236B006', 'sw3223A003', 'sw3268A015', 'sw3228B002', 'sw3254A017', 'sw3296A013', 'sw3232A012', 'sw3228A001', 'sw3228B016', 'sw3205B004', 'sw3290B015', 'sw3242B008', 'sw3283A000', 'sw3255B005', 'sw3223A012', 'sw3266A009', 'sw3290B004', 'sw3286A005', 'sw3200A004', 'sw3239B010', 'sw3237A014', 'sw3268A001', 'sw3255B015', 'sw3225A013', 'sw3216A006', 'sw3257B007', 'sw3228A009', 'sw3245B013', 'sw3235A006', 'sw3200A012', 'sw3294B011', 'sw3254A002', 'sw3214A005', 'sw3201B003', 'sw3293A016', 'sw3219A005', 'sw3245B014', 'sw3255B011', 'sw3260A002', 'sw3233A012', 'sw3270A010', 'sw3231A001', 'sw3229A011', 'sw3257B006', 'sw3238B001', 'sw3204A010', 'sw3201B012', 'sw3237A013', 'sw3257B001', 'sw3231A010', 'sw3214A004', 'sw3237B004', 'sw3226A007', 'sw3201B017', 'sw3255B006', 'sw3271B008', 'sw3255B007', 'sw3254A001', 'sw3245B003', 'sw3205B008', 'sw3236B012', 'sw3259A001', 'sw3270B002', 'sw3245B009', 'sw3245A006', 'sw3282B009', 'sw3233B006', 'sw3225B006', 'sw3236B003', 'sw3269A005', 'sw3259A000', 'sw3223B009', 'sw3268A006', 'sw3293A003', 'sw3269A002', 'sw3231A004', 'sw3225A014', 'sw3294B012', 'sw3225B003', 'sw3283A007', 'sw3293A013', 'sw3200A011', 'sw3280B006', 'sw3256B011', 'sw3245A007', 'sw3225B011', 'sw3250B005', 'sw3250B008', 'sw3214A011', 'sw3230B000', 'sw3294B004', 'sw3246B012', 'sw3204A004', 'sw3244B011', 'sw3266A004', 'sw3254A006', 'sw3231A003', 'sw3237B002', 'sw3236B008', 'sw3236B014', 'sw3235A009', 'sw3228A007', 'sw3296A012', 'sw3231A011', 'sw3242A015', 'sw3201B006', 'sw3294B005', 'sw3237B000', 'sw3225B012', 'sw3276B013', 'sw3293A008', 'sw3200A007', 'sw3275B013', 'sw3225A003', 'sw3268A009', 'sw3288B002', 'sw3250B014', 'sw3245A014', 'sw3236B011', 'sw3230B007', 'sw3268A010', 'sw3225B005', 'sw3266A013', 'sw3216A010', 'sw3290B002', 'sw3254A004', 'sw3254A000', 'sw3225A010', 'sw3228A004']
c33 = ['sw3340B009', 'sw3363B015', 'sw3368A011', 'sw3363B010', 'sw3328B002', 'sw3346B012', 'sw3346B014', 'sw3369B006', 'sw3319A008', 'sw3333A011', 'sw3319A010', 'sw3362A001', 'sw3389B000', 'sw3360B009', 'sw3363B001', 'sw3375B010', 'sw3351B008', 'sw3371A010', 'sw3327A001', 'sw3327B002', 'sw3373B004', 'sw3373A014', 'sw3359B005', 'sw3326B005', 'sw3333B007', 'sw3324A019', 'sw3333B004', 'sw3352A018', 'sw3326B008', 'sw3363B012', 'sw3379A017', 'sw3354A012', 'sw3315A005', 'sw3354B007', 'sw3331B000', 'sw3317A009', 'sw3373B002', 'sw3389B004', 'sw3310A013', 'sw3324B002', 'sw3340B014', 'sw3333B008', 'sw3324A015', 'sw3373B007', 'sw3340B004', 'sw3351B000', 'sw3361B013', 'sw3342A002', 'sw3367B011', 'sw3371B002', 'sw3354A007', 'sw3338B014', 'sw3333A010', 'sw3319B007', 'sw3326A003', 'sw3313B008', 'sw3349B002', 'sw3363B005', 'sw3304B012', 'sw3331A007', 'sw3343B014', 'sw3325A014', 'sw3354A013', 'sw3306A001', 'sw3368A012', 'sw3333B005', 'sw3313B000', 'sw3317B013', 'sw3326B003', 'sw3352A002', 'sw3389B012', 'sw3328B006', 'sw3319A000', 'sw3354A000', 'sw3306B003', 'sw3304B008', 'sw3373B010', 'sw3317B010', 'sw3349B006', 'sw3345A000', 'sw3344A008', 'sw3345B013', 'sw3333A014', 'sw3326A013', 'sw3383B003', 'sw3327A010', 'sw3319A009', 'sw3389B002', 'sw3331B008', 'sw3359B006', 'sw3383B015', 'sw3327A008', 'sw3317B007', 'sw3306B009', 'sw3328B007', 'sw3383B008', 'sw3334A002', 'sw3361A004', 'sw3315A007', 'sw3310A005', 'sw3325A006', 'sw3332B006', 'sw3365B001', 'sw3367B007', 'sw3363B018', 'sw3363A001', 'sw3398A002', 'sw3326B002', 'sw3342A003', 'sw3326B009', 'sw3363B007', 'sw3317B012', 'sw3338B005']
c34 = ['sw3451B012', 'sw3447B005', 'sw3419B013', 'sw3458A008', 'sw3464A004', 'sw3467B007', 'sw3458A004', 'sw3457A015', 'sw3403A012', 'sw3447B006', 'sw3424A007', 'sw3447B001', 'sw3411B010', 'sw3454A008', 'sw3451B006', 'sw3424B004', 'sw3439A009', 'sw3467B004', 'sw3467B013', 'sw3448A013', 'sw3403A010', 'sw3424A001', 'sw3417B009', 'sw3467A010', 'sw3424B003', 'sw3457A010', 'sw3426B013', 'sw3489A013', 'sw3419B007', 'sw3443B000', 'sw3419A000', 'sw3467B000', 'sw3496A012', 'sw3454B008', 'sw3489A010', 'sw3445A013', 'sw3411A000', 'sw3453A002', 'sw3420B000', 'sw3441B011', 'sw3426B002', 'sw3496A001', 'sw3496A011', 'sw3411B005', 'sw3439B006', 'sw3447B003', 'sw3443B004', 'sw3457A004', 'sw3443B009', 'sw3429A013', 'sw3431B003', 'sw3419B008', 'sw3467B008', 'sw3496A003', 'sw3491A010', 'sw3467B012', 'sw3449B003', 'sw3443B006', 'sw3426B012', 'sw3445A009', 'sw3448A005', 'sw3457B012', 'sw3414B010', 'sw3445A005', 'sw3473A000', 'sw3447A002', 'sw3454B003', 'sw3439A001', 'sw3419B009', 'sw3419B005', 'sw3429A010', 'sw3419A010', 'sw3453A009', 'sw3431A011', 'sw3496A000', 'sw3450A015', 'sw3443B012', 'sw3443B013', 'sw3414B000', 'sw3402A015', 'sw3448B009', 'sw3489B000', 'sw3454B004', 'sw3491B001', 'sw3496A009', 'sw3464B006', 'sw3419A005', 'sw3460A004', 'sw3420B008', 'sw3467A000', 'sw3420B014', 'sw3424A012', 'sw3431A012', 'sw3420B001', 'sw3451B015', 'sw3443B002', 'sw3450A011', 'sw3460B006', 'sw3431A014', 'sw3429A009', 'sw3457A002', 'sw3489A012', 'sw3450A007']
c35 = ['sw3596A009', 'sw3550A011', 'sw3527A008', 'sw3535B001', 'sw3503B014', 'sw3523B007', 'sw3517B010', 'sw3550B005', 'sw3508B000', 'sw3587A011', 'sw3503A009', 'sw3527A010', 'sw3500A007', 'sw3565B006', 'sw3570A004', 'sw3574A002', 'sw3513A012', 'sw3509B000', 'sw3524A003', 'sw3539A017', 'sw3596B000', 'sw3595A012', 'sw3596B010', 'sw3584B014', 'sw3539A006', 'sw3563B002', 'sw3513A007', 'sw3535A005', 'sw3524A012', 'sw3503A014', 'sw3596A005', 'sw3580A010', 'sw3527A007', 'sw3587B002', 'sw3504A000', 'sw3596B006', 'sw3503A011', 'sw3508B002', 'sw3584B013', 'sw3527A005', 'sw3517B007', 'sw3527A006', 'sw3570A013', 'sw3567B015', 'sw3513A006', 'sw3539A015', 'sw3500A009', 'sw3523B006', 'sw3527A001', 'sw3550B002', 'sw3595A008', 'sw3524A002', 'sw3517A007', 'sw3508B004', 'sw3565B012', 'sw3523B002', 'sw3595A001', 'sw3504A004', 'sw3524A004', 'sw3503B013', 'sw3595A005', 'sw3503A008', 'sw3574A012', 'sw3526A004', 'sw3563B001', 'sw3550B009', 'sw3567B007', 'sw3584B006', 'sw3503A000', 'sw3503A012', 'sw3550B010', 'sw3527B011', 'sw3523B012', 'sw3595A004', 'sw3523B015', 'sw3523B003', 'sw3563B010', 'sw3526A002', 'sw3527B004', 'sw3595B010', 'sw3576A010', 'sw3563B000', 'sw3524A006', 'sw3539A011', 'sw3539A003', 'sw3500B005', 'sw3513A015', 'sw3554B012', 'sw3576B015', 'sw3539A018', 'sw3513A013', 'sw3539A000', 'sw3539A002', 'sw3539A019', 'sw3576B010', 'sw3554B009', 'sw3556A008', 'sw3543B004', 'sw3524B000', 'sw3576B011', 'sw3596B013']
c36 = ['sw3659A013', 'sw3660A008', 'sw3647B001', 'sw3688B010', 'sw3697A010', 'sw3663A006', 'sw3682A005', 'sw3636A009', 'sw3666A012', 'sw3688A012', 'sw3659A009', 'sw3659A011', 'sw3657A006', 'sw3615B005', 'sw3688B013', 'sw3686A009', 'sw3639A013', 'sw3647A004', 'sw3657A014', 'sw3682A016', 'sw3659B007', 'sw3626B005', 'sw3639A003', 'sw3615B002', 'sw3659A010', 'sw3639A004', 'sw3666A000', 'sw3694B011', 'sw3665A004', 'sw3688B012', 'sw3657A007', 'sw3666A004', 'sw3659A005', 'sw3666A011', 'sw3624A002', 'sw3694A007', 'sw3624A007', 'sw3639A001', 'sw3615B001', 'sw3659A000', 'sw3639A010', 'sw3665A011', 'sw3636A006', 'sw3691A013', 'sw3663A005', 'sw3688B006', 'sw3663B007', 'sw3607A012', 'sw3665A002', 'sw3639A012', 'sw3615B006', 'sw3639A000', 'sw3691A001', 'sw3686B005', 'sw3636B001', 'sw3682A001', 'sw3660A009', 'sw3663A013', 'sw3694A003', 'sw3659B002', 'sw3636B010', 'sw3682B000', 'sw3639A008', 'sw3638A009', 'sw3682A010', 'sw3624A001', 'sw3651A011', 'sw3688B002', 'sw3686B012', 'sw3638A005', 'sw3665A012', 'sw3663A003', 'sw3659B001', 'sw3692B001', 'sw3694A013', 'sw3607A013', 'sw3682A013', 'sw3676A011', 'sw3682A002', 'sw3633B001', 'sw3666A003', 'sw3665A010', 'sw3639A002', 'sw3682A011', 'sw3691B011', 'sw3691B008', 'sw3658A000', 'sw3666A008', 'sw3688B009', 'sw3694A008', 'sw3647A003', 'sw3657B002', 'sw3607A003', 'sw3699A007', 'sw3696A007', 'sw3633B007', 'sw3647A002', 'sw3682A006', 'sw3659A006', 'sw3624A010', 'sw3642A005']
c37 = ['sw3798A014', 'sw3703A010', 'sw3716A002', 'sw3788A006', 'sw3751A009', 'sw3728A004', 'sw3750B009', 'sw3798A001', 'sw3711A002', 'sw3703B000', 'sw3709A005', 'sw3756A002', 'sw3768A007', 'sw3796A015', 'sw3777A003', 'sw3777B008', 'sw3728B004', 'sw3725A008', 'sw3797B011', 'sw3781B011', 'sw3760B011', 'sw3720A017', 'sw3777A000', 'sw3798A010', 'sw3716A013', 'sw3723A014', 'sw3797B010', 'sw3777B006', 'sw3798A015', 'sw3781A016', 'sw3777B010', 'sw3746B011', 'sw3796B010', 'sw3728A009', 'sw3707B010', 'sw3728B005', 'sw3709A006', 'sw3798A013', 'sw3754B003', 'sw3797A011', 'sw3723B013', 'sw3750A008', 'sw3736B002', 'sw3745B001', 'sw3768B001', 'sw3738A009', 'sw3745A007', 'sw3725B000', 'sw3773B005', 'sw3720A012', 'sw3746B010', 'sw3734A006', 'sw3716A012', 'sw3768B009', 'sw3703B009', 'sw3743A010', 'sw3720A009', 'sw3743A017', 'sw3768B002', 'sw3769B011', 'sw3754B012', 'sw3756A008', 'sw3769B002', 'sw3784B002', 'sw3764A009', 'sw3774A004', 'sw3725B009', 'sw3784A013', 'sw3768B010', 'sw3768A000', 'sw3709A000', 'sw3743A013', 'sw3756A004', 'sw3747A010', 'sw3716A011', 'sw3709B014', 'sw3774B004', 'sw3750A016', 'sw3720A018', 'sw3709B006', 'sw3798A000', 'sw3707A014', 'sw3788A004', 'sw3796B013', 'sw3747A011', 'sw3798A016', 'sw3798A009', 'sw3736A006', 'sw3798B012', 'sw3791A003', 'sw3709B011', 'sw3725A004', 'sw3746A013', 'sw3764B010', 'sw3774B007', 'sw3754B004', 'sw3754B009', 'sw3727A000', 'sw3720A005', 'sw3756A011', 'sw3796A014', 'sw3707A008', 'sw3769B007', 'sw3760B015', 'sw3725A002', 'sw3720A003', 'sw3716B009', 'sw3720A016', 'sw3769B012', 'sw3711A003', 'sw3797A012', 'sw3788A019', 'sw3798A007', 'sw3738A005', 'sw3750A000', 'sw3798B013', 'sw3711A000', 'sw3728A006', 'sw3720A010', 'sw3747A016', 'sw3723A004']
c38 = ['sw3821B005', 'sw3801A012', 'sw3845A011', 'sw3862B008', 'sw3830B006', 'sw3862A004', 'sw3845B004', 'sw3847B014', 'sw3804B008', 'sw3850A010', 'sw3883B013', 'sw3815B011', 'sw3801A002', 'sw3845B008', 'sw3830A000', 'sw3804B007', 'sw3811A010', 'sw3887A012', 'sw3847B008', 'sw3862B000', 'sw3845A015', 'sw3830A011', 'sw3802B000', 'sw3825B004', 'sw3802A001', 'sw3862A000', 'sw3825B008', 'sw3876B011', 'sw3821B012', 'sw3845B003', 'sw3847B013', 'sw3805B005', 'sw3876B010', 'sw3876B007', 'sw3845A013', 'sw3804B010', 'sw3810B002', 'sw3804B005']
c39 = ['sw3911B000', 'sw3988A010', 'sw3902A000', 'sw3988A005', 'sw3988A003', 'sw3988A016', 'sw3988A011', 'sw3902A003', 'sw3952B000', 'sw3917A009', 'sw3921B000', 'sw3917A012']
c40 = ['sw4036A013', 'sw4019B007', 'sw4078A011', 'sw4060B011', 'sw4022B006', 'sw4019B004', 'sw4078A005', 'sw4004A010', 'sw4080B017', 'sw4078A003', 'sw4092B006', 'sw4080B005', 'sw4037A014', 'sw4022A007', 'sw4019B006', 'sw4080B016', 'sw4078A014', 'sw4019B014', 'sw4078A001', 'sw4077B003', 'sw4037A010', 'sw4077A010', 'sw4077A011', 'sw4022A012', 'sw4037A000', 'sw4077B006', 'sw4080B000', 'sw4072B016', 'sw4019B005']
c41 = ['sw4166A004', 'sw4154A009', 'sw4166A017', 'sw4149B000', 'sw4149B010', 'sw4166A016', 'sw4168A004', 'sw4166A006', 'sw4168A012', 'sw4184B008', 'sw4168A010', 'sw4168A003', 'sw4152B003', 'sw4166A015', 'sw4127B002', 'sw4133B011', 'sw4152A000', 'sw4166A014', 'sw4154A011', 'sw4174A004', 'sw4153A002', 'sw4168A008', 'sw4147A002', 'sw4129B003', 'sw4168A001', 'sw4153A010', 'sw4154B010', 'sw4113A009', 'sw4154A005', 'sw4153A011']
c42 = []
c43 = ['sw4380B013', 'sw4330B001', 'sw4353A005', 'sw4318B002', 'sw4363B013', 'sw4330B002', 'sw4314B005', 'sw4346A015', 'sw4318B011', 'sw4329B012', 'sw4314B010', 'sw4376B005', 'sw4346A004', 'sw4353B003', 'sw4356A003', 'sw4318A015', 'sw4372A007', 'sw4314B015']
c44 = []
c45 = ['sw4572A013', 'sw4519B001', 'sw4548A005', 'sw4565B010', 'sw4548A008']
c46 = ['sw4691A002', 'sw4697A019', 'sw4697A014', 'sw4697A007', 'sw4633A006', 'sw4691A000', 'sw4633A000', 'sw4633A007', 'sw4691A012', 'sw4682B012', 'sw4659A005', 'sw4646A013', 'sw4697A006', 'sw4691A007']
c47 = ['sw4707A009', 'sw4728A009', 'sw4796A016', 'sw4736A001', 'sw4799A002', 'sw4759A007', 'sw4785A002', 'sw4774A010', 'sw4799B012', 'sw4728A015', 'sw4721B015', 'sw4759A002', 'sw4785A014', 'sw4723A006', 'sw4728A012', 'sw4721B006', 'sw4785A000', 'sw4796A018', 'sw4774A011', 'sw4721B005', 'sw4796A004', 'sw4716B010', 'sw4707A007', 'sw4759A005', 'sw4765A005', 'sw4736A007', 'sw4785B013', 'sw4796A010', 'sw4725B011', 'sw4721B001', 'sw4752B000', 'sw4765A006', 'sw4721B012', 'sw4796A012']
c48 = ['sw4859A003', 'sw4886A012', 'sw4856A010', 'sw4859A011', 'sw4890B008', 'sw4886A004', 'sw4868B005', 'sw4868A007', 'sw4829A006', 'sw4868B007', 'sw4801A008', 'sw4858A009', 'sw4802A011', 'sw4856A006', 'sw4821A006', 'sw4840A011', 'sw4834A001', 'sw4858A001', 'sw4840A008', 'sw4801A001', 'sw4880A002']
c49 = ['sw4927A006', 'sw4928A009', 'sw4908A006', 'sw4902A016', 'sw4940A012', 'sw4905A004', 'sw4905A007', 'sw4905B010', 'sw4927A009', 'sw4902A005', 'sw4936A007']

controversial_files = c20 + c21 + c22 + c23 + c24 + c25 + c26 + c27 + c28 + c29 + c30 + c31 + c32 + c33 + c34 + c35 + c36 + c37 + c38 + c39 + c40 + c41 + c42 + c43 + c44 + c45 + c46 + c47 + c48 + c49
