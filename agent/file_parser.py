import os

class SfoldParser:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.data = {}

    def parse_file(self, filename):
        filepath = os.path.join(self.input_dir, filename)
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            return lines
        except FileNotFoundError:
            print(f"Warning: {filename} not found in {self.input_dir}")
            return []

    def parse_structure_files(self):
        # Parse key structure prediction files.
        structure_data = {}
        structure_data['10structure.out'] = self.parse_file('10structure.out')
        structure_data['10structure_2.out'] = self.parse_file('10structure_2.out')
        structure_data['ecentroid.ct'] = self.parse_file('ecentroid.ct')
        structure_data['ecentroid.bp'] = self.parse_file('ecentroid.bp')
        self.data['structure'] = structure_data

    def parse_cluster_files(self):
        # Parse files from the clusters directory.
        clusters_dir = os.path.join(self.input_dir, 'clusters')
        clusters_data = {}
        if os.path.isdir(clusters_dir):
            for file in os.listdir(clusters_dir):
                if file.endswith('.ct') or file.endswith('.bp') or file.endswith('.list'):
                    # Use the absolute path to the file in clusters directory
                    file_path = os.path.join(clusters_dir, file)
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    clusters_data[file] = lines
            self.data['clusters'] = clusters_data
        else:
            print("Warning: clusters directory not found")

    def parse_energy_files(self):
        # Parse energy-related files.
        energy_files = ['fe.out', 'smfe.out']
        energy_data = {}
        for file in energy_files:
            energy_data[file] = self.parse_file(file)
        self.data['energy'] = energy_data

    def parse_statistical_files(self):
        # Parse statistical analysis files.
        stats_files = ['cdf.out', 'bp.dist.from.ecentroid.out']
        stats_data = {}
        for file in stats_files:
            stats_data[file] = self.parse_file(file)
        self.data['stats'] = stats_data

    def parse_accessibility_files(self):
        # Parse accessibility-related files.
        accessibility_files = ['oligo.out', 'oligo_f.out', 'bp.out', 'sstrand.out']
        accessibility_data = {}
        for file in accessibility_files:
            accessibility_data[file] = self.parse_file(file)
        self.data['accessibility'] = accessibility_data

    def parse_all(self):
        self.parse_structure_files()
        self.parse_cluster_files()
        self.parse_energy_files()
        self.parse_statistical_files()
        self.parse_accessibility_files()
        return self.data