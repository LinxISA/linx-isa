## 函数简介
此配置文件显示了每个基准测试中函数的执行比率 `cycles`。仅列出总周期超过 `1%` 的函数。
实验在`x86-Xeon8158`上进行。使用的编译器是`ICC 7.5.0`，编译选项为`-O3`。
这些数据是通过Perf（Linux性能分析工具）获得的，并且是根据过程中不同功能的周期比率来收集的。

>使用的perf命令：
>perf record -o /path/perf.data --call-graph lbr -g cmd（每个基准测试的运行命令）

## INT 基准
### 600.perlbench_s
- 运行命令
```
./perlbench_s -I ../../run/run_base_refspeed_mytest-m64.0000/lib/ ../../run/run_base_refspeed_mytest-m64.0000/checkspam.pl 2500 5 25 11 150 1 1 1 1
```
- 性能报告
```
Children    Self	Function
99.81%	    5.42%	Perl_runops_standard
99.74%	    0.00%	main
99.74%	    0.00%	perl_run
27.95%	    2.64%	Perl_pp_entersub
25.52%	    0.00%	XS_HTML__Parser_parse
25.51%	    0.00%	parse
25.45%	    0.19%	parse_buf
25.12%	    0.43%	report_event
24.85%	    2.27%	Perl_regexec_flags
22.46%	    0.19%	Perl_call_sv
22.12%	    2.25%	Perl_pp_match
16.35%	    0.18%	parse_start
13.66%	    11.48%	S_regmatch
8.88%	    1.92%	S_find_byclass
8.09%	    4.20%	Perl_leave_scope
7.23%	    2.48%	Perl_pp_multideref
6.91%	    5.22%	Perl_hv_common
6.20%	    3.68%	Perl_sv_setsv_flags
4.89%	    0.30%	Perl_sv_free2
4.77%	    0.40%	Perl_pp_subst
4.58%	    2.17%	Perl_sv_clear
3.72%	    1.30%	Perl_pp_nextstate
3.57%	    0.37%	Perl_sv_grow
3.25%	    1.12%	Perl_re_intuit_start
3.18%	    0.75%	Perl_pp_aassign
3.17%	    0.71%	Perl_pp_leavesub
3.09%	    0.68%	Perl_sv_catpvn_flags
2.82%	    2.36%	_int_malloc
2.80%	    0.40%	Perl_pop_scope
2.78%	    0.34%	Perl_pp_sassign
2.76%	    0.18%	Perl_pp_return
2.60        1.87%	Perl_pp_padsv
2.57%	    0.03%	Perl_pp_goto
2.52%	    0.10%	Perl_pp_regcomp
2.48%	    2.41%	S_dofindlabel
2.42%	    2.36%	Perl_sv_upgrade
2.39%	    2.34%	Perl_fbm_instr
2.29%	    0.12%	Perl_re_op_compile
2.25%	    0.15%	_init
2.19%	    0.05%	Perl_safesysrealloc
2.13%	    0.18%	__libc_realloc
2.12%	    0.43%	Perl_sv_setpvn
2.10        0.45%	Perl_free_tmps
2.02%	    0.26%	Perl_pp_push
2.00%	    0.39%	Perl_pp_concat
1.94%	    0.33%	_int_realloc
1.93%	    0.06%	Perl_safesysmalloc
1.90%	    0.91%	Perl_pp_method_named
1.86%	    0.74%	__malloc
1.78%	    0.12%	Perl_hv_clear
1.77%	    0.15%	Perl_pp_substcont
1.68%	    0.02%	Perl_pp_trans
1.60%	    1.59%	Perl_do_trans
1.53%	    0.11%	S_regtry
1.42%	    0.13%	Perl_pp_sort
1.41%	    0.09%	Perl_pp_anoncode
1.40%	    1.40%	__memcpy_avx_unaligned_erms
1.39%	    1.13%	Perl_pp_and
1.36%	    0.20%	Perl_cv_undef
1.30%	    0.38%	Perl_pp_split
1.24%	    0.56%	S_mergesortsv
1.22%	    0.14%	Perl_safesysfree
1.21%	    0.44%	Perl_sv_force_normal_flags
1.11%	    0.13%	S_concat_pat
1.05%	    0.71%	S_regrepeat.isra.11
1.04%	    0.23%	S_cv_clone_pad
1.03%	    1.03%	__free
1.03%	    0.06%	Perl_do_kv
1.02%	    0.10%	Perl_sv_catsv_flags
```

### 602.gcc_s
- 运行命令
```
./gcc_s ../../run/run_base_refspeed_gcc7.3.0-static-O3-64.0000/gcc-pp.c -O5 -fipa-pta -o ../../run/run_base_refspeed_gcc7.3.0-static-O3-64.0000/gcc-pp.opts-O5_-fipa-pta.s
```
- 性能报告
```
Children    Self	Function
63.36%	    4.25%	solve_graph
57.23%	    55.35%	bitmap_ior_into
40.49%	    0.06%	solve_constraints
31.68%	    0.02%	execute_pass_list
30.74%	    0.02%	execute_one_pass
11.70%	    0.00%	tree_rest_of_compilation
10.15%	    0.00%	cgraph_expand_function
9.74%	    0.00%	cgraph_optimize.part.12
6.14%	    0.02%	df_analyze
5.65%	    0.00%	df_analyze_problem
4.62%	    0.11%	rest_of_handle_ira
3.23%	    3.08%	bitmap_set_bit
2.95%	    0.04%	execute_pre
2.95%	    0.64%	df_worklist_dataflow
2.51%	    0.01%	execute_function_todo
2.44%	    0.01%	execute_todo
2.21%	    0.07%	cse_main
1.86%	    0.08%	execute_rtl_cprop
1.66%	    0.00%	rest_of_handle_sched2
1.66%	    0.01%	schedule_insns.part.20
1.45%       0.19%	compute_antic
1.45%	    0.13%	reload
1.37%	    1.03%	_int_malloc
1.35%	    0.02%	if_convert
1.33%	    0.06%	rest_of_handle_dse
1.30%	    0.00%	execute_ipa_pass_list
1.19%	    0.02%	execute_rtl_pre
1.19%	    0.20%	cse_insn
1.16%	    0.21%	__libc_malloc
1.16%	    0.89%	bitmap_elt_insert_after
1.13%	    0.01%	ira_build
1.10%	    0.06%	rest_of_handle_combine
1.09%	    0.00%	df_lr_finalize
1.09%	    0.04%	xmalloc
1.07%	    0.26%	fast_dce
1.07%	    0.00%	rest_of_handle_cse
1.04%	    0.78%	bitmap_and_compl
1.00%	    0.02%	gimple_expand_cfg
```

### 605.mcf_s
- 运行命令
```
./mcf ../../run/run_base_refspeed_mytest-m64.0000/inp.in
```
- 性能报告
```
Children    Self	Function
98.84%	    0.00%	global_opt
65.15%	    0.00%	main
65.15%	    0.00%	__libc_start_main
56.92%	    0.00%	primal_net_simplex
56.58%	    0.07%	master.constprop.0
54.70%	    21.74%	primal_bea_mpp
47.77%	    17.82%	spec_qsort
40.02%	    23.41%	price_out_impl
22.64%	    0.00%	_start
20.71%	    19.30%	cost_compare
11.05%	    10.65%	arc_compare
2.54%	    2.29%	suspend_impl
1.43%	    1.43%	marc_arcs
1.04%	    1.04%	update_tree
```

### 620.omnetpp_s
- 运行命令
```
./omnetpp_s ../../run/run_base_refspeed_mytest-m64.0000/omnetpp.ini
```
- 性能报告
```
Children    Self	Function
100.00%	    0.00%  	eat
100.00%     0.00%  	EnvirBase::run
100.00%     0.00%  	Cmdenv::run
99.91%      0.29%  	Cmdenv::simulate
93.79%      0.90%  	cSimulation::doOneEvent
48.32%      2.27%  	EtherMAC::handleMessage
20.27%      0.64%  	cMessageHeap::removeFirst
17.98%      0.20%  	MACRelayUnitNP::handleMessage
17.85%      17.82%	cMessageHeap::shiftup
17.65%      0.12%  	MACRelayUnitNP::processFrame
13.58%      0.82%  	EtherMAC::handleEndRxPeriod
12.48%      1.15%  	EtherMACBase::frameReceptionComplete
12.33%      1.21%  	EtherMAC::startFrameTransmission
11.19%      7.03%  	cGate::deliver
9.79%       0.07%  	EtherMAC::handleEndTxPeriod
9.44%       9.40%  	std::_Rb_tree_increment
8.98%       0.07%  	MACRelayUnitBase::handleAndDispatchFrame
8.32%       0.20%  	MACRelayUnitBase::printAddressTable
8.03%       0.31%  	EtherFrameWithLLC::dup
7.84%       1.07%  	cSimpleModule::sendDelayed
6.88%       0.47%  	EtherMACBase::handleEndTxPeriod
6.75%       0.59%  	cSimpleModule::sendDelayed
6.61%       2.77%  	cOutVector::record
6.04%       1.73%  	cDatarateChannel::deliver
5.78%       0.10%  	EtherHub::handleMessage
5.49%       2.42%  	__dynamic_cast
5.47%       0.03%  	EtherFrameWithLLC::~EtherFrameWithLLC
5.41%       5.33%  	free
5.18%       4.91%  	cSimulation::selectNextModule
4.28%       0.11%  	operator new
4.19%       0.92%  	__malloc
3.79%       0.19%  	EnvirBase::recordInOutputVector
3.59%       3.59%  	cIndexedFileOutputVectorManager::record
3.49%       0.06%  	cNamedObject::~cNamedObject
3.44%       0.01%  	operator delete[]
3.35%       2.86%  	cQueue::pop
3.24%       3.22%  	_int_malloc
3.21%       1.97%  	__cxxabiv1::__si_class_type_info::__do_dyncast
3.09%       0.45%  	EtherMAC::processMsgFromNetwork
3.08%       1.31%  	cNamedObject::setName
2.86%       1.87%  	cSimpleModule::scheduleAt
2.35%       0.36%  	cSimpleModule::arrived
2.32%       0.29%  	_init
2.12%       0.61%  	cObject::drop
2.11%       1.42%  	cModule::gate
2.06%       0.33%  	EtherMACBase::processFrameFromUpperLayer
2.00%       0.07%  	MACRelayUnitBase::updateTableWithAddress
1.79%       1.59%  	cPacket::operator=
1.50%       1.49%  	cGate::getId
1.44%       1.40%  	cDefaultList::doInsert
1.38%       1.14%  	cMessageHeap::insert
1.37%       1.37%  	__strcmp_sse2_unaligned
1.30%       0.67%  	cQueue::insert
1.25%       0.14%  	MACRelayUnitBase::removeAgedEntriesFromTable
1.19%       0.04%  	cSimulation::insertMsg
1.05%       0.98%  	EtherMAC::printState

```
### 623.xalancbmk_s
- 运行命令
```
./xalancbmk_s -v ../../run/run_base_refspeed_mytest-m64.0000/t5.xml ../../run/run_base_refspeed_mytest-m64.0000/xalanc.xsl
```
- 性能报告
```
Children    Self    Function
77.84%      0.00%   xalanc_1_10::XSLTEngineImpl::process
77.84%      0.00%   xalanc_1_10::StylesheetRoot::process
77.84%      0.75%   xalanc_1_10::ElemTemplateElement::execute
55.59%      0.34%   xalanc_1_10::XObjectFactoryDefault::doReturnObject
54.89%      39.66%  xalanc_1_10::XStringCachedAllocator::destroy
39.34%      0.19%   xalanc_1_10::ElemWithParam::startElement
38.99%      0.41%   xalanc_1_10::XPath::executeMore
37.96%      0.48%   xalanc_1_10::XPath::runFunction
32.49%      0.02%   xalanc_1_10::ElemCallTemplate::endElement
32.45%      0.08%   xalanc_1_10::VariablesStack::popContextMarker
22.04%      0.01%   xercesc_2_7::IGXMLScanner::scanContent
20.85%      19.20%  xercesc_2_7::ValueStore::contains
16.54%      0.04%   xercesc_2_7::IGXMLScanner::scanStartTagNS
15.99%      0.03%   xercesc_2_7::IdentityConstraintHandler::activateIdentityConstraint
15.94%      0.02%   xercesc_2_7::SelectorMatcher::startElement
15.89%      0.10%   xercesc_2_7::XPathMatcher::startElement
15.75%      0.00%   xercesc_2_7::FieldMatcher::matched
15.75%      0.01%   xercesc_2_7::ValueStore::addValue
15.18%      0.07%   xalanc_1_10::XStringCached::~XStringCached
15.03%      8.54%   xalanc_1_10::XalanDOMStringCache::release
8.93%       0.44%   xalanc_1_10::XalanDOMString::append
8.57%       0.01%   xalanc_1_10::StylesheetExecutionContextDefault::releaseCachedString
7.55%       6.99%   xalanc_1_10::XalanVector<unsigned short, xalanc_1_10::MemoryManagedConstructionTraits<unsigned short> >::insert
6.43%       5.78%   xalanc_1_10::ReusableArenaAllocator<xalanc_1_10::XalanDOMString>::destroyObject
6.17%       0.26%   xalanc_1_10::FunctionSubstring::execute
5.34%       0.02%   xercesc_2_7::IGXMLScanner::scanEndTag
5.22%       0.01%   xercesc_2_7::IdentityConstraintHandler::deactivateContext
4.99%       0.11%   xalanc_1_10::FunctionConcat::execute
3.79%       0.00%   xercesc_2_7::ValueStore::endDcocumentFragment
2.50%       0.40%   xalanc_1_10::VariablesStack::findXObject
2.14%       0.34%   xalanc_1_10::XPath::variable
1.98%       0.80%   xalanc_1_10::VariablesStack::findEntry
1.77%       1.64%   xercesc_2_7::NameDatatypeValidator::compare
1.74%       0.22%   xalanc_1_10::StylesheetExecutionContextDefault::getVariable
1.69%       0.03%   xercesc_2_7::MemoryManagerImpl::allocate
1.64%       0.05%   operator new
1.60%       0.19%   xalanc_1_10::ElemChoose::startElement
1.58%       0.45%   malloc
1.36%       0.10%   xalanc_1_10::XPath::executeMore
1.34%       0.00%   xercesc_2_7::ValueStoreCache::transplant
1.34%       0.00%   xercesc_2_7::ValueStore::append
1.29%       0.05%   xalanc_1_10::XPath::executeMore
1.24%       0.04%   xalanc_1_10::XPath::equals
1.17%       0.09%   xalanc_1_10::StylesheetExecutionContextDefault::getParamVariable
1.13%       1.08%   _int_malloc
1.12%       0.03%   xalanc_1_10::XObjectFactoryDefault::createString
1.12%       0.09%   xalanc_1_10::XPath::functionStringLength
1.08%       0.55%   xalanc_1_10::XalanReferenceCountedObject::removeReference
1.05%       0.09%   xalanc_1_10::XalanVector<unsigned short, xalanc_1_10::MemoryManagedConstructionTraits<unsigned short> >::XalanVector
1.03%       0.53%   xalanc_1_10::XStringCachedAllocator::createString

```

### 625.x264_s
- 运行命令
```
./x264_s --pass 1 --stats ../../run/run_base_refspeed_mytest-m64.0001/x264_stats.log --bitrate 1000 --frames 1000 -o ../../run/run_base_refspeed_mytest-m64.0001/BuckBunny.264  ../../run/run_base_refspeed_mytest-m64.0001/BuckBunny.yuv  1280x720
```
- 性能报告
```
Children    Self    Function
100.00%     0.00%   __libc_start_main
100.00%     0.00%   _start
100.00%     0.00%   main
99.96%      0.00%   x264_encoder_encode
50.32%      0.14%   x264_slice_write
44.99%      0.00%   x264_lookahead_get_frames
44.21%      0.00%   x264_slicetype_analyse
41.40%      0.00%   x264_slicetype_decide
40.97%      1.33%   x264_slicetype_mb_cost.isra.20
38.06%      1.55%   x264_me_search_ref
33.23%      0.31%   x264_macroblock_analyse
27.27%      0.04%   x264_slicetype_frame_cost.constprop.26
26.90%      26.81%  x264_pixel_satd_8x4
26.24%      1.46%   refine_subpel
19.90%      0.45%   x264_pixel_satd_8x8
17.89%      0.01%   x264_slicetype_frame_cost
10.45%      0.62%   x264_macroblock_probe_skip
8.58%       8.56%   x264_pixel_sad_x4_8x8
8.15%       8.11%   quant_4x4
7.77%       7.71%   get_ref
7.65%       0.18%   x264_pixel_satd_16x16
7.15%       0.01%   x264_fdec_filter_row
5.72%       0.44%   x264_macroblock_encode
5.24%       0.00%   x264_frame_filter
5.23%       5.23%   hpel_filter
5.04%       5.04%   x264_pixel_sad_x4_16x16
5.00%       0.06%   x264_weights_analyse
4.59%       4.58%   sub4x4_dct
3.80%       0.12%   x264_mb_analyse_intra
3.52%       0.06%   sub8x8_dct
2.90%       2.89%   x264_pixel_sad_16x16
2.84%       2.81%   x264_pixel_sad_8x8
2.70%       0.08%   x264_mb_mc_01xywh
2.10%       0.00%   scenecut_internal
2.09%       2.08%   mc_chroma
1.83%       0.17%   x264_frame_deblock_row
1.79%       0.01%   x264_frame_init_lowres
1.75%       1.75%   x264_pixel_var_16x16
1.68%       1.67%   frame_init_lowres_core
1.57%       0.15%   x264_adaptive_quant_frame
1.19%       0.17%   x264_macroblock_write_cabac
1.19%       0.65%   x264_macroblock_cache_load
1.13%       0.59%   x264_macroblock_tree_propagate
1.12%       0.01%   sub16x16_dct
1.02%       0.14%   x264_mb_encode_8x8_chroma

```

### 631.deepsjeng_s
- 运行命令
```
./deepsjeng_s ../../run/run_base_refspeed_mytest-m64.0000/ref.txt
```
- 性能报告
```
Children    Self    Function
99.67%      10.10%  search
43.28%      8.89%   qsearch
23.29%      1.94%   eval
21.14%      8.68%   feval
20.72%      20.49%  ProbeTT
13.09%      0.00%   search_root
10.49%      5.80%   see
10.25%      0.11%   search
7.53%       4.30%   order_moves
5.18%       5.08%   make
4.07%       3.55%   FindFirstRemove
3.59%       0.00%   think
3.57%       2.79%   attacks_to
3.53%       1.99%   gen_captures
3.00%       0.03%   qsearch
2.84%       0.67%   check_legal
2.77%       2.71%   RookAttacks
2.64%       2.61%   StoreTT
2.61%       0.00%   run_epd_testsuite
2.52%       1.49%   gen
2.43%       2.41%   unmake
2.22%       1.83%   is_attacked
2.17%       2.10%   BishopAttacks
2.08%       1.82%   PopCount
2.02%       1.89%   ThickPopCount
2.00%       0.13%   gen_evasions
1.43%       1.23%   in_check
1.33%       0.60%   gen_good_checks
1.21%       0.98%   compact_move
1.09%       1.01%   static_pawn_eval
```

### 641.leela_s
- 运行命令
```
./leela ../../run/run_base_refspeed_mytest-m64.0000/ref.sgf
```
- 性能报告
```
Children    Self    Function
99.90%      0.31%   UCTSearch::think
99.49%      0.00%   main
97.65%      0.10%   UCTSearch::play_simulation
90.04%      1.84%   Playout::run
84.57%      11.00%  FastState::play_random_move
17.56%      16.61%  FastBoard::update_board_fast
14.02%      4.20%   FastState::walk_empty_list
12.03%      9.99%   FastBoard::add_pattern_moves
10.33%      0.05%   FastState::play_random_move
8.39%       7.35%   FastBoard::save_critical_neighbours
6.53%       3.40%   FastBoard::self_atari
6.04%       6.03%   FastBoard::self_atari
5.85%       5.68%   FastBoard::no_eye_fill
5.44%       5.29%   FastBoard::get_pattern_fast_augment
5.18%       5.18%   FastBoard::nbr_criticality
4.86%       0.00%   __libc_start_main
4.80%       0.00%   _start
3.88%       3.88%   UCTNode::uct_select_child
3.50%       3.18%   Random::randint
3.00%       2.79%   FastBoard::fast_ss_suicide
2.60%       2.50%   Matcher::matches
2.32%       1.09%   Random::get_Rng
2.31%       1.34%   UCTNode::updateRAVE
1.26%       0.03%   Playout::mc_owner
1.06%       0.62%   FastBoard::get_extra_dir
```

### 648.exchange2_s
- 运行命令
```
./exchange2_s 0/1/6
```
- 性能报告
```
Children    Self    Function
100.00%     0.00%   _start
100.00%     0.00%   __libc_start_main
100.00%     0.00%   main
100.00%     0.06%   MAIN__
99.93%      0.55%   __brute_force_MOD_brute
76.74%      76.50%  __brute_force_MOD_digits_2
22.57%      3.33%   __logic_MOD_new_solver
13.55%      5.78%   specific.3547
6.92%       0.01%   _gfortran_mminloc0_4_i4@plt
6.91%       6.91%   _gfortran_mminloc0_4_i4
3.92%       3.92%   hidden_triplets.3539
3.83%       0.00%   eliminate.9643
1.69%       1.69%   naked_triplets.3541
```

### 657.xz_s
- 运行命令
```
./xz_s ../../run/run_base_refspeed_mytest-m64.0000/cpu2006docs.tar.xz 6643 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1036078272 1111795472 4
```
- 性能报告
```
Children    Self    Function
100.00%     0.00%   _start
100.00%     0.00%   __libc_start_main
100.00%     0.00%   main
95.81%      0.00%   lzma_code
89.86%      0.00%   spec_compress
89.86%      0.00%   compressStream
89.77%      0.00%   stream_encode
89.77%      0.00%   block_encode
89.18%      0.00%   lz_encode
89.05%      0.01%   lzma2_encode
89.04%      9.45%   lzma_lzma_encode
79.49%      13.66%  lzma_lzma_optimum_normal
42.90%      9.15%   lzma_mf_bt4_skip
33.96%      33.81%  bt_skip_func
22.95%      0.77%   lzma_mf_find
22.23%      6.76%   lzma_mf_bt4_find
15.34%      15.32%  bt_find_func
6.15%       0.00%   uncompressStream
6.14%       0.00%   spec_uncompress
6.04%       0.00%   stream_decode
6.03%       0.00%   block_decode
5.48%       0.00%   lz_decode
5.47%       0.01%   lzma2_decode
5.46%       5.25%   lzma_decode
3.77%       0.01%   sha_process
3.38%       3.38%   sha_compress
2.03%       0.00%   spec_mem_load
1.88%       0.00%   spec_mem_sum
1.13%       0.00%   lzma_check_update
1.13%       1.13%   lzma_crc64
1.07%       0.01%   _init
```

- - -