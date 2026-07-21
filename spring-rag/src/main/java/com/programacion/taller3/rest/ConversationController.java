package com.programacion.taller3.rest;

import com.programacion.taller3.models.ChatMessage;
import com.programacion.taller3.models.Conversation;
import com.programacion.taller3.services.ConversationService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Controller REST para gestionar conversaciones persistentes.
 * Provee endpoints CRUD para listar, obtener historial y eliminar conversaciones.
 */
@RestController
@RequestMapping("/api/conversations")
public class ConversationController {

    private final ConversationService conversationService;

    public ConversationController(ConversationService conversationService) {
        this.conversationService = conversationService;
    }

    /**
     * Lista todas las conversaciones guardadas.
     */
    @GetMapping
    public ResponseEntity<List<Conversation>> listConversations() {
        return ResponseEntity.ok(conversationService.listConversations());
    }

    /**
     * Obtiene el historial de mensajes de una conversación.
     */
    @GetMapping("/{id}/messages")
    public ResponseEntity<List<ChatMessage>> getMessages(@PathVariable String id) {
        return ResponseEntity.ok(conversationService.getMessages(id));
    }

    /**
     * Elimina una conversación y todos sus mensajes.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteConversation(@PathVariable String id) {
        conversationService.deleteConversation(id);
        return ResponseEntity.noContent().build();
    }
}
