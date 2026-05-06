import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService, DocumentDetail, Sentence } from '../api.service';

@Component({
  selector: 'app-document-label',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './document-label.component.html',
  styleUrl: './document-label.component.css',
})
export class DocumentLabelComponent implements OnInit {
  clauseTypes: string[] = [];
  document: DocumentDetail | null = null;
  loading = false;
  error = '';

  constructor(
    private readonly api: ApiService,
    private readonly route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    this.api.getClauseTypes().subscribe((types) => (this.clauseTypes = types));
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isFinite(id)) {
      this.error = 'Invalid document id.';
      return;
    }
    this.loadDocument(id);
  }

  loadDocument(id: number): void {
    this.loading = true;
    this.error = '';
    this.api.getDocument(id).subscribe({
      next: (document) => {
        this.document = document;
        this.loading = false;
      },
      error: () => {
        this.error = 'Could not open document.';
        this.loading = false;
      },
    });
  }

  updateSentenceLabel(sentence: Sentence, clauseType: string): void {
    const nextLabel = clauseType || null;
    this.api.setLabel(sentence.id, nextLabel).subscribe({
      next: (updated) => {
        sentence.clause_type = updated.clause_type;
        if (this.document) {
          this.recalculateCounts(this.document);
        }
      },
      error: () => (this.error = 'Could not update clause label.'),
    });
  }

  private recalculateCounts(document: DocumentDetail): void {
    const counts: Record<string, number> = {};
    for (const type of this.clauseTypes) {
      counts[type] = 0;
    }

    let labeled = 0;
    for (const sentence of document.sentences) {
      if (sentence.clause_type) {
        labeled += 1;
        counts[sentence.clause_type] = (counts[sentence.clause_type] ?? 0) + 1;
      }
    }

    document.labeled_count = labeled;
    document.clause_counts = counts;
  }
}
