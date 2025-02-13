src/
└── chromatographicpeakpicking/
├── **init**.py
├── core/ # Abstract design patterns
│ ├── **init**.py
│ ├── builders/
│ │ ├── **init**.py
│ │ └── pipeline_builder.py
│ ├── domain/ # Domain models
│ │ ├── **init**.py
│ │ ├── building_block.py
│ │ ├── chromatogram.py
│ │ ├── hierarchy.py
│ │ ├── peak.py
│ │ └── peptide.py
│ ├── factories/
│ │ ├── **init**.py
│ │ ├── analyzer_factory.py
│ │ ├── corrector_factory.py
│ │ ├── detector_factory.py
│ │ └── pipeline_factory.py
│ ├── protocols/
│ │ ├── **init**.py
│ │ ├── analyzable.py
│ │ ├── configurable.py
│ │ ├── correctable.py
│ │ ├── detectable.py
│ │ ├── error_handler.py
│ │ ├── observable.py
│ │ ├── parseable.py
│ │ ├── selectable.py
│ │ ├── serializable.py
│ │ ├── validatable.py
│ │ └── visualizable.py
│ ├── singletons/
│ │ ├── **init**.py
│ │ └── singleton.py
│ ├── strategies/ # Strategy pattern for analyzers and other strategies
│ │ ├── **init**.py
│ │ ├── base_analyzer.py
│ │ └── peak_analyzer.py
│ ├── types/ # Custom types, errors, and validation logic
│ ├── **init**.py
│ ├── config.py
│ ├── errors.py
│ └── validation.py
├── implementations/ # Concrete implementations for various functions
│ ├── **init**.py
│ ├── analyzers/ # Concrete analyzers
│ │ ├── **init**.py
│ │ ├── chromatogram_analyzer.py
│ │ ├── peak_analyzer.py
│ │ └── split_tree_analysis.py
│ ├── baseline_correction/ # Baseline correction algorithms
│ │ ├── **init**.py
│ │ ├── aals.py
│ │ └── swm.py
│ ├── detectors/ # Concrete detectors
│ │ ├── **init**.py
│ │ └── peak_detector.py
│ ├── peak_detection/ # Peak detection algorithms
│ │ ├── **init**.py
│ │ └── peak_finder.py
│ ├── peak_selection/ # Peak selection implementations
│ │ ├── **init**.py
│ │ ├── Ipeak_picker.py
│ │ ├── classic_chrome.py
│ │ ├── hierarchical_sgppm.py
│ │ ├── peak_finder.py
│ │ └── sgppm.py
│ ├── pipelines/ # Concrete pipeline implementations
│ │ ├── **init**.py
│ │ ├── cc_pipeline.py
│ │ ├── sgppm_pipeline.py
│ │ └── hsgppm_pipeline.py
│ ├── builders/ # Concrete pipeline builders
│ │ ├── **init**.py
│ │ └── concrete_pipeline_builder.py
│ ├── commands/ # Command classes for pipeline stages
│ │ ├── **init**.py
│ │ ├── baseline_command.py
│ │ └── detection_command.py
│ ├── observers/ # Observer classes for monitoring pipelines
│ │ ├── **init**.py
│ │ └── progress_observer.py
│ ├── serializers/ # Concrete serializers
│ │ ├── **init**.py
│ │ └── peak_serializer.py
│ ├── visualizers/ # Concrete visualizers
│ ├── **init**.py
│ ├── chromatogram_visualizer.py
│ └── image_type.py
├── config/ # Configuration management
│ ├── **init**.py
│ ├── config_manager.py
│ └── global_config.py
├── io/ # Input and output operations
│ ├── **init**.py
│ ├── formats/ # Format handlers for CSV, Excel, etc.
│ │ ├── **init**.py
│ │ ├── csv_format.py
│ │ ├── excel_format.py
│ │ └── format_handler.py
│ ├── protocols/ # Reader and writer interfaces
│ │ ├── **init**.py
│ │ ├── reader.py
│ │ └── writer.py
│ ├── readers/ # Data readers
│ │ ├── **init**.py
│ └── writers/ # Data writers
│ ├── **init**.py
├── utils/ # Utility functions and modules
│ ├── **init**.py
│ ├── gaussian_curve.py
│ └── process_sequence_count_chromatogram_data.py
├── visualization/ # Visualization components
│ ├── **init**.py
│ ├── exporters/ # Export visualization results
│ │ ├── **init**.py
│ └── renderers/ # Render visualizations
│ ├── **init**.py
├── infrastructure/ # Infrastructure-related components
│ ├── **init**.py
│ ├── caching/ # Caching mechanisms
│ │ ├── **init**.py
│ │ └── result_cache.py
│ ├── logging/ # Logging mechanisms
│ │ ├── **init**.py
│ │ ├── analysis_logger.py
│ │ └── performance_logger.py
│ ├── metrics/ # Metrics collection
│ │ ├── **init**.py
│ │ ├── chromatogram_metrics.py
│ │ └── performance_metrics.py
│ └── persistence/ # Data persistence mechanisms
│ ├── **init**.py
│ ├── base_repository.py
│ ├── chromatogram_repository.py
│ └── peak_repository.py
├── parsers/ # Data parsers
│ ├── **init**.py
│ └── tabular_data_parser.py
