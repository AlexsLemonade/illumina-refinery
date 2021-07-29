from ccdlstaging/dr_affymetrix:latest

USER root
RUN Rscript -e 'install.packages("optparse")'
RUN mkdir /out && chown user /out
USER user

COPY scrape_brainarray_genes.R .

ENTRYPOINT [ "Rscript", "scrape_brainarray_genes.R" ]
