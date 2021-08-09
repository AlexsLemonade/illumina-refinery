# Illumina Refinery

A workflow for selecting which gene ID to map a given probe ID to in the case
where a given probe maps to multiple genes.

## Methods

To determine which gene to map a given probe to, we select the genes in order of priority as follows:

- Pick the gene with the most appearances in Brainarray packages for Affymetrix platforms of the same species as the input Illumina platform
- If two or more of the associated gene IDs appear an equal number of times in
  Brainarray platforms, or if none of the associated gene IDs appear in any Brainarray platform, we break ties as follows:
  - First, we check Ensembl and filter out any gene IDs that are no longer valid
  - Next, if there are any genes on the main assembly, we take only the genes on the main assembly and discard genes on alternate assemblies.
  - If there are still two or more genes left, we pick the gene with the lowest gene ID to break the tie.

The workflow is split up into the following steps:

### 00 Scraping Illumina

For each Illumina platform we are interested in, we do the following:

- Load relevant Bioconductor package
- Load the probe-to-gene mappings into a data frame
- Filter the data frame so that the remaining columns are all probe IDs which appear more than once
- Output the data frame as a TSV file for each platform

### 01 Scraping Brainarray

This section of the workflow counts the number of times each gene ID appears among all the brainarray packages for a given species, and outputs this count as a TSV file for the three species with Illumina platforms we are interested in.

### 02 Selecting Gene IDs

This step reads in the outputs from the previous steps and applies the prioritization from above to determine how to map each probe ID. The output is given as a TSV file for each platform so that we can use the results on refine.bio.

## Running the workflow

To run the full workflow, if you have Docker and make installed you can just run `make` or `make all`.

The Makefile is set up to cache the outputs of individual steps of the workflow and to detect changes to the files associated with a particular step. It also understands the dependencies between steps, so if you edit a file in the `00_scraping_illumina` directory it will re-run only steps 00 and 02 of the pipeline.

## Copyright

`identifier-refinery` output assets are released under a [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/legalcode) license. All code is released under the BSD 3-clause license.

Input assets in step 00 come from the the [Bioconductor project](http://bioconductor.org/):

- Mark Dunning, Andy Lynch and Matthew Eldridge (2021). illuminaHumanv1.db: Illumina HumanWG6v1 annotation data (chip illuminaHumanv1). R package version 1.26.0.
- Mark Dunning, Andy Lynch and Matthew Eldridge (2021). illuminaHumanv2.db: Illumina HumanWG6v2 annotation data (chip illuminaHumanv2). R package version 1.26.0.
- Mark Dunning, Andy Lynch and Matthew Eldridge (2021). illuminaHumanv3.db: Illumina HumanHT12v3 annotation data (chip illuminaHumanv3). R package version 1.26.0.
- Mark Dunning, Andy Lynch and Matthew Eldridge (2021). illuminaHumanv4.db: Illumina HumanHT12v4 annotation data (chip illuminaHumanv4). R package version 1.26.0.
- Mark Dunning, Andy Lynch and Matthew Eldridge (2021). illuminaMousev1.db: Illumina MouseWG6v1 annotation data (chip illuminaMousev1). R package version 1.26.0.
- Mark Dunning, Andy Lynch and Matthew Eldridge (2021). illuminaMousev1p1.db: Illumina MouseWG6v1p1 annotation data (chip illuminaMousev1p1). R package version 1.26.0.
- Mark Dunning, Andy Lynch and Matthew Eldridge (2021). illuminaMousev2.db: Illumina MouseWG6v2 annotation data (chip illuminaMousev2). R package version 1.26.0.
- Mark Dunning, Andy Lynch and Matthew Eldridge (2021). illuminaRatv1.db: Illumina Ratv1 annotation data (chip illuminaRatv1). R package version 1.26.0.

Other assets used in the computing of step 01 come from the [Brainarray project](http://brainarray.mbni.med.umich.edu/Brainarray/Database/CustomCDF/genomic_curated_CDF.asp):

- Manhong Dai, Pinglang Wang, Andrew D. Boyd, Georgi Kostov, Brian Athey, Edward G. Jones, William E. Bunney, Richard M. Myers, Terry P. Speed, Huda Akil, Stanley J. Watson and Fan Meng. Evolving gene/transcript definitions significantly alter the interpretation of GeneChip data. Nucleic Acid Research 33 (20), e175, 2005.

and in step 02 we use gene ID information from the [Ensembl project](http://ensembl.org):

- Kevin L Howe, Premanand Achuthan, James Allen, Jamie Allen, Jorge Alvarez-Jarreta, M Ridwan Amode, Irina M Armean, Andrey G Azov, Ruth Bennett, Jyothish Bhai, Konstantinos Billis, Sanjay Boddu, Mehrnaz Charkhchi, Carla Cummins, Luca Da Rin Fioretto, Claire Davidson, Kamalkumar Dodiya, Bilal El Houdaigui, Reham Fatima, Astrid Gall, Carlos Garcia Giron, Tiago Grego, Cristina Guijarro-Clarke, Leanne Haggerty, Anmol Hemrom, Thibaut Hourlier, Osagie G Izuogu, Thomas Juettemann, Vinay Kaikala, Mike Kay, Ilias Lavidas, Tuan Le, Diana Lemos, Jose Gonzalez Martinez, José Carlos Marugán, Thomas Maurel, Aoife C McMahon, Shamika Mohanan, Benjamin Moore, Matthieu Muffato, Denye N Oheh, Dimitrios Paraschas, Anne Parker, Andrew Parton, Irina Prosovetskaia, Manoj P Sakthivel, Ahamed I Abdul Salam, Bianca M Schmitt, Helen Schuilenburg, Dan Sheppard, Emily Steed, Michal Szpak, Marek Szuba, Kieron Taylor, Anja Thormann, Glen Threadgold, Brandon Walts, Andrea Winterbottom, Marc Chakiachvili, Ameya Chaubal, Nishadi De Silva, Bethany Flint, Adam Frankish, Sarah E Hunt, Garth R IIsley, Nick Langridge, Jane E Loveland, Fergal J Martin, Jonathan M Mudge, Joanella Morales, Emily Perry, Magali Ruffier, John Tate, David Thybert, Stephen J Trevanion, Fiona Cunningham, Andrew D Yates, Daniel R Zerbino, and Paul Flicek. Ensembl 2021. Nucleic Acids Res. 2021, vol. 49(1):884–891. PubMed PMID: 33137190. doi:10.1093/nar/gkaa942
