"""
For each Illumina platform that we support:
  - Read the dataframe of duplicate probes and the different gene IDs
  - Read the brainarray occurrence counts for the current species
  - Group the duplicate probes dataframe by probe ID
  - Pick the gene with the most appearances in Brainarray packages for Affymetrix platforms of the same species as the input Illumina platform
  - If none of the associated gene IDs appear in any Brainarray platform, an NA is emitted
  - If two or more of the associated gene IDs appear an equal number of times in
    Brainarray platforms, or if none of the associated gene IDs appear in any Brainarray platform, we break ties as follows:
    - First, we check Ensembl and filter out any gene IDs that are no longer valid
    - Next, if there are any genes on the main assembly, we take only the genes on the main assembly and discard genes on alternate assemblies.
    - If there are still two or more genes left, we pick the gene with the lowest gene ID to break the tie.
"""

import pandas as pd
import requests

ILLUMINA_PLATFORMS = [
    ("illuminaHumanv1", "Homo sapiens"),
    ("illuminaHumanv2", "Homo sapiens"),
    ("illuminaHumanv3", "Homo sapiens"),
    ("illuminaHumanv4", "Homo sapiens"),
    ("illuminaMousev1", "Mus musculus"),
    ("illuminaMousev1p1", "Mus musculus"),
    ("illuminaMousev2", "Mus musculus"),
    ("illuminaRatv1", "Rattus norvegicus"),
]


def pick_gene_id(species: str):
    brainarray_occurrence_counts = pd.read_csv(
        f"/out/01_scraping_brainarray_genes/{species.replace(' ', '_')}.tsv",
        sep="\t",
        index_col="mapped_gene_ids",
    )

    karyotype = requests.get(
        f"""https://rest.ensembl.org/info/assembly/{
            species.lower().replace(' ', '_')
        }?content-type=application/json"""
    ).json()["karyotype"]

    def brainarray_occurrences(gene: str) -> int:
        try:
            return brainarray_occurrence_counts.loc[gene]["n"]
        except KeyError:
            return 0

    def aggregator(args):
        occurrences = [(gene, brainarray_occurrences(gene)) for gene in args.astype(str)]

        nonzero_occurrences = [o for o in occurrences if o[1] > 0]

        if len(nonzero_occurrences) == 1:
            return nonzero_occurrences[0][0]
        elif len(nonzero_occurrences) > 1:
            # If we have some non-zero occurrences, we will only focus on those
            max_num_occurrences = max(nonzero_occurrences, key=lambda x: x[1])[1]
            max_occurrences = [o for o in occurrences if o[1] == max_num_occurrences]
            if len(max_occurrences) == 1:
                return max_occurrences[0][0]

            # This filter failed, let's try another one
            genes = [o[0] for o in max_occurrences]
        else:
            # If everything occurs 0 times, we will need to try another filter method
            genes = [o[0] for o in occurrences]

        # Now we have a tie. We need to gather more information on the genes in order ot progress.
        def get_gene_info(gene):
            return requests.get(
                f"https://rest.ensembl.org/lookup/id/{gene}?expand=1;content-type=application/json"
            ).json()

        genes = [(g, get_gene_info(g)) for g in genes]

        # The first thing to check is that the gene IDs are
        # valid, because there is at least one case of a tie (ENSG00000157654,
        # ENSG00000243444) where one of the gene IDs is now retired.
        def is_valid(gene, gene_info):
            # Ensembl responds to requests for an invalid gene ID with an error message.
            if set(gene_info.keys()) == {"error"}:
                print(f"  > Filtered tied gene {gene} because it has an invalid/outdated ID.")
                return False

            return True

        valid_genes = [g for g in genes if is_valid(*g)]
        if len(valid_genes) == 1:
            return valid_genes[0][0]
        elif len(valid_genes) == 0:
            # If there aren't any valid gene IDs, then it's not worth mapping to anything
            return None

        # Now break ties by checking whether one of the genes is on the main
        # assembly. There are a lot of cases of ties like (ENSG00000165714,
        # ENSG00000280689) where one gene is on the main assembly and the other
        # is an alternate-assembly allele.
        def is_on_main_assembly(gene, gene_info):
            # If an object is on the main assembly, "seq_region_name" is the
            # name of the chromosome that the gene comes from. If it is not,
            # then it is the name of the alternative sequence that the gene
            # comes from. `karyotype` only has the names of the chromosomes, so
            # an object is on the main assembly iff its seq_region_name is in
            # the karyotype.
            #
            # Inspired by the check that the Ensembl website does:
            # https://github.com/Ensembl/ensembl-webcode/blob/a76b7a77bc13962ea9f157a2ffe467eca05ec676/modules/EnsEMBL/Web/Object.pm#L256
            return gene_info["seq_region_name"] in karyotype

        main_assembly_genes = [g for g in valid_genes if is_on_main_assembly(*g)]
        if len(main_assembly_genes) == 1:
            return main_assembly_genes[0][0]
        elif len(main_assembly_genes) == 0:
            tied_genes = valid_genes
        else:
            tied_genes = main_assembly_genes

        # Finally, if we still have a tie, we pick the one with the lower gene ID.
        # This is an arbitrary but consistent way to pick one gene when we have
        # exhausted all of the other metrics.
        lowest_id = min(tied_genes, key=lambda x: x[0])[0]
        print(
            f"  > We have a tie: {', '.join(g[0] for g in tied_genes)}.\n"
            f"    Picking the one with lowest ID: {lowest_id}."
        )
        return lowest_id

    return aggregator


for platform, species in ILLUMINA_PLATFORMS:
    print(f"Processing platform {platform}...")
    duplicate_probe_ids = pd.read_csv(f"/out/00_scraping_illumina/{platform}.tsv", sep="\t")

    (
        duplicate_probe_ids.groupby("probe_id", as_index=False)
        .aggregate({"ensembl_id": pick_gene_id(species)})
        .to_csv(f"/out/02_selecting_gene_ids/{platform}.tsv", index=False, sep="\t")
    )
